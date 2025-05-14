from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from database.cities import muslim_countries,get_cities_for_country
import math
from database.databse import surah_repo
import requests

def choose_country():
    kb = InlineKeyboardBuilder()

    for country, code in muslim_countries.items():
        kb.button(text=country, callback_data=f"country_{code}")

    kb.adjust(2)  # Show 2 countries per row
    return kb.as_markup()
def choose_city(country, start=0, limit=9, current_page=1):
    kb = InlineKeyboardBuilder()

    country_code = muslim_countries.get(country)  # Convert country name to code
    if not country_code:
        return kb.as_markup()  # Return empty markup if the country is not found

    cities = get_cities_for_country(country_code)  # Fetch cities correctly
    # total_pages = (len(cities) + 8) // 9  # Calculate total pages
    total_pages = math.ceil(len(cities) / 9)
    for city in cities[start:limit]:
        kb.button(text=city, callback_data=f"location_{city.replace(' ', '_')}:{country_code}")

    kb.adjust(3)  # Arrange buttons in 3 columns

    pagination_buttons = []
    if current_page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(text='⏪ Oldingi (Назад)',
                                 callback_data=f'prev_page:{country}:{start}:{limit}:{current_page}')
        )

    pagination_buttons.append(InlineKeyboardButton(text=f'{current_page}/{total_pages}', callback_data='current'))

    if current_page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(text='Keyingi ⏩ (Вперёд)',
                                 callback_data=f'next_page:{country}:{start}:{limit}:{current_page}:{total_pages}')
        )

    if pagination_buttons:
        kb.row(*pagination_buttons)

    return kb.as_markup()

def set_reminder():
    kb = InlineKeyboardBuilder()
    kb.button(text='Eslatma(Напоминание',callback_data='eslatma')

    return kb.as_markup()

def take_off_reminder():
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Eslatmani o‘chirish (Удалить напоминание)", callback_data="remove_eslatma")

    return kb.as_markup()

def choose_surah(start=0, limit=18,current_page=1):
    kb = InlineKeyboardBuilder()

    surah_list = surah_repo.get_surah_name()[start:limit]

    for surah_id, surah_name in surah_list:
        kb.button(text=f"{surah_id}. {surah_name}", callback_data=f"surah_:{surah_id}:{surah_name}")
    kb.adjust(3)
    total_pages = math.ceil(len(surah_repo.get_surah_name()) / 18)

    pagination_buttons = []
    if current_page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(text='⏪ Oldingi (Назад)',
                                 callback_data=f'surah_prev_page:{start}:{limit}:{current_page}')
        )

    pagination_buttons.append(InlineKeyboardButton(text=f'{current_page}/{total_pages}', callback_data='current_surah'))

    if current_page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(text='Keyingi ⏩ (Вперёд)',
                                 callback_data=f'surah_next_page:{start}:{limit}:{current_page}:{total_pages}')
        )

    if pagination_buttons:
        kb.row(*pagination_buttons)

    return kb.as_markup()



