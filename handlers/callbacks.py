from aiogram.types import CallbackQuery,Message
from aiogram import Router,F
from keyboards.inline import choose_city,choose_country,set_reminder,take_off_reminder,choose_surah
import requests
from database.databse import users_repo,praying_repo,surah_repo
from datetime import datetime,timedelta
from aiogram import Bot
import asyncio
import pytz
from database.cities import get_cities_for_country,muslim_countries

prayer_tasks = {}

url = "http://api.aladhan.com/v1/timingsByCity"

router = Router()

country_codes_to_names = {code: country for country, code in muslim_countries.items()}


@router.callback_query(F.data.startswith('country_'))
async def user_selected_country(call: CallbackQuery):
    country_code = call.data.replace("country_", "")  # Extract country code (e.g., "UZ")

    if country_code not in country_codes_to_names:
        return await call.answer("Mavjud emas! (Не существует!)", show_alert=True)

    country_name = country_codes_to_names[country_code]  # Convert code to name

    await call.message.edit_text(
        text=f"{country_name} dagi shaharni tanlang (Выберите город в {country_name})",
        reply_markup=choose_city(country_name)
    )


@router.callback_query(F.data.startswith('next_page'))
async def next_page(call: CallbackQuery):
    data = call.data.split(':')

    if len(data) != 6:  # Ensure data has all required parts
        return await call.answer("Xatolik! (Ошибка!)", show_alert=True)

    _, country, start, limit, page, total_pages = data
    start, limit, page, total_pages = map(int, [start, limit, page, total_pages])

    if page == total_pages:
        return await call.answer('Ohirgi bet (Последняя страница)', show_alert=True)

    await call.message.edit_reply_markup(
        reply_markup=choose_city(
            country=country,
            start=start + 9,
            limit=limit + 9,
            current_page=page + 1,
        )
    )


@router.callback_query(F.data.startswith('prev_page'))
async def prev_page(call: CallbackQuery):
    data = call.data
    __,country, start, finish, page = data.split(':')

    if int(page) == 1:
        return await call.answer('Siz birinchi bettasiz (Вы на первой странице)', show_alert=True)

    await call.message.edit_reply_markup(
        reply_markup=choose_city(
            country=country,
            start=int(start) - 9,
            limit=int(finish) - 9,
            current_page=int(page) - 1,
        )
    )


@router.callback_query(F.data.startswith('location_'))
async def user_chose_location(call: CallbackQuery):
    location = call.data.replace("location_", "").replace("_", " ")
    city, country_code = location.rsplit(":", 1)
    city = city.replace("_", " ")
    country = country_codes_to_names.get(country_code, "Unknown")

    params = {
        "city": city,
        "country": country,
        "method": 2,
        'school': 1
    }

    response = requests.get(url=url, params=params)
    response.raise_for_status()
    data = response.json()

    timings = data['data']['timings']
    timezone = data["data"]["meta"]["timezone"]
    day = data['data']['date']['readable']
    hijri_day = data['data']['date']['hijri']['date']

    user_id = users_repo.get_user(chat_id=call.from_user.id)
    current_datetime = datetime.now().strftime("%Y-%m-%d")

    fajr = timings.get("Fajr")
    dhuhr = timings.get("Dhuhr")
    asr = timings.get("Asr")
    maghrib = timings.get("Maghrib")
    isha = timings.get("Isha")

    praying_repo.add_praying(
        location=f"{city} {country}",
        fajr=fajr,
        dhuhr=dhuhr,
        asr=asr,
        maghrib=maghrib,
        isha=isha,
        created_at=current_datetime,
        timezone=timezone,
        user_id=user_id[0]
    )

    await call.message.answer(
        text=f'🕌 Namoz vaqtlari ({city}, {country}) - {day} (Hijri {hijri_day})\n\n'
             f'Fajr: {fajr}\n'
             f'Dhuhr: {dhuhr}\n'
             f'Asr: {asr}\n'
             f'Maghrib: {maghrib}\n'
             f'Isha: {isha}\n\n'
             '⏳ Namoz vaqtlariga eslatma qo‘yishni xohlaysizmi? (Хотите установить напоминание?)',
        reply_markup=set_reminder()
    )

async def send_prayer_reminder(bot: Bot, chat_id: int, prayer_name: str):

    await bot.send_message(chat_id,
                           f"🕌 {prayer_name} namozi vaqti yaqinlashmoqda! ({prayer_name} время намаза приближается!)")


async def schedule_prayer_reminders(bot: Bot, chat_id: int, prayer_times: dict, user_timezone: str):
    """Schedules daily prayer reminders for a user."""

    # ✅ Cancel all existing reminders properly
    if chat_id in prayer_tasks:
        for task in prayer_tasks[chat_id]:  # Loop through each task
            task.cancel()
        del prayer_tasks[chat_id]  # Remove user entry

    async def reminder_loop():
        while True:
            now_utc = datetime.now(pytz.utc)
            user_tz = pytz.timezone(user_timezone)


            for prayer_name, time_str in prayer_times.items():
                prayer_time = datetime.strptime(time_str, "%H:%M")

                # Adjust prayer time
                prayer_time = now_utc.astimezone(user_tz).replace(
                    hour=prayer_time.hour,
                    minute=prayer_time.minute,
                    second=0,
                    microsecond=0
                ) + timedelta(minutes=8)
                prayer_time = prayer_time if prayer_time.tzinfo else user_tz.localize(prayer_time)
                prayer_time_utc = prayer_time.astimezone(pytz.utc)

                reminder_time = prayer_time_utc - timedelta(minutes=10)
                delay = (reminder_time - now_utc).total_seconds()

                if delay > 0:
                    await asyncio.sleep(delay)
                    await send_prayer_reminder(bot, chat_id, prayer_name)

            await asyncio.sleep(86400)  # Wait for 24 hours before repeating

    # ✅ Store all new reminder tasks properly
    tasks = [asyncio.create_task(reminder_loop())]
    prayer_tasks[chat_id] = tasks

async def send_reminder_after_delay(bot: Bot, chat_id: int, prayer_name: str, delay: float):
    """Waits for the delay and sends a prayer reminder."""
    await asyncio.sleep(delay)
    await send_prayer_reminder(bot, chat_id, prayer_name)

@router.callback_query(F.data.startswith('eslatma'))
async def set_prayer_reminder(call: CallbackQuery, bot: Bot):
    bot = call.bot
    user_id = users_repo.get_user(chat_id=call.from_user.id)
    user_prayer_times = praying_repo.get_praying(user_id=user_id[0])

    if not user_prayer_times:
        return await call.answer("Siz namoz vaqtlarini saqlamadingiz! (Вы не сохранили время намаза!)", show_alert=True)

    prayer_times = {
        "Bomdod (Fajr)": user_prayer_times["Fajr"],
        "Peshin (Dhuhr)": user_prayer_times["Dhuhr"],
        "Asr": user_prayer_times["Asr"],
        "Shom (Maghrib)": user_prayer_times["Maghrib"],
        "Xufton (Isha)": user_prayer_times["Isha"]
    }
    user_timezone = user_prayer_times["Timezone"]

    if call.from_user.id in prayer_tasks :
        await call.message.answer(
            "❗Yangi eslatma qoyish uchun eskisini ochiring\n\n"
            "❗Eslatmalarni o‘chirish uchun quyidagi tugmani bosing.",
            reply_markup=take_off_reminder()
        )
        return

    await call.message.answer(
        "✅ Namoz eslatmalari yoqildi! (Напоминания о намазе включены!)\n\n"
        "❗ Eslatmalarni o‘chirish uchun quyidagi tugmani bosing.",
        reply_markup=take_off_reminder()
    )

    asyncio.create_task(schedule_prayer_reminders(bot, call.from_user.id, prayer_times, user_timezone))


@router.callback_query(F.data == "remove_eslatma")
async def remove_prayer_reminder(call: CallbackQuery):
    """Removes scheduled prayer reminders for a user."""
    user_id = call.from_user.id

    if user_id in prayer_tasks:
        # Cancel all tasks stored for this user
        for task in prayer_tasks[user_id]:
            task.cancel()

        # Remove the user from the dictionary
        del prayer_tasks[user_id]

        await call.message.edit_text("❌ Namoz eslatmalari o'chirildi! (Напоминания о намазе удалены!)")
    else:
        await call.answer("Sizda hozircha eslatmalar yo'q! (У вас нет активных напоминаний!)", show_alert=True)

@router.callback_query(F.data.startswith('surah_next_page'))
async def next_page_surah(call:CallbackQuery):
    data = call.data.split(':')

    if len(data) != 5:  # Ensure data has all required parts
        return await call.answer("Xatolik! (Ошибка!)", show_alert=True)

    _, start, limit, page, total_pages = data
    start, limit, page, total_pages = map(int, [start, limit, page, total_pages])

    if page == total_pages:
        return await call.answer('Ohirgi bet (Последняя страница)', show_alert=True)

    await call.message.edit_reply_markup(
        reply_markup=choose_surah(
            start=start + 18,
            limit=limit + 18,
            current_page=page + 1,
        )
    )

@router.callback_query(F.data.startswith('surah_prev_page'))
async def prev_page_surah(call:CallbackQuery):
    data = call.data.split(':')

    if len(data) != 4:  # Ensure data has all required parts
        return await call.answer("Xatolik! (Ошибка!)", show_alert=True)

    _, start, limit, page = data
    start, limit, page = map(int, [start, limit, page])

    if int(page) == 1:
        return await call.answer('Siz birinchi bettasiz (Вы на первой странице)', show_alert=True)

    await call.message.edit_reply_markup(
        reply_markup=choose_surah(
            start=start - 18,
            limit=limit - 18,
            current_page=page - 1,
        )
    )

@router.callback_query(F.data.startswith('surah_'))
async def user_chose_surah(call:CallbackQuery):
    _, surah_number,surah_name = call.data.split(':')
    ayahs = surah_repo.get_full_surah(surah_number)
    ayahs_transliteration = surah_repo.get_surah_transliteration(surah_number)
    ayah_text = "\n".join([f"{index + 1}. {ayah}" for index, ayah in enumerate(ayahs)])
    ayah_text_transliteration = "\n".join([f"{index + 1}. {ayah}" for index, ayah in enumerate(ayahs_transliteration)])
    await call.message.answer(text=surah_repo.get_surah_info(surah_name))

    async def send_large_message(text):
        chunk_size = 4096
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        for chunk in chunks:
            await call.message.answer(chunk)

    await send_large_message(ayah_text)
    await send_large_message(f"Uzbekcha oqilish varianti:\n\n{ayah_text_transliteration}")

