from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import CommandStart,Command
from keyboards.reply import start_kb
from database.databse import users_repo,surah_repo

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    surah_repo.add_surah()
    chat_id = message.from_user.id
    users_repo.add_user(chat_id=chat_id)
    await message.answer("Muslim Botiga xush kelibsiz. Davom etish uchun pastki tugmalardan birnini bosing.\n--------------------------------------------\nWelcome to Muslim Bot press one of the lower buttons to proceed",
                         reply_markup=start_kb())

@router.message(Command(commands='info'))
async def info(message: Message):
    await message.answer(
        'Ushbu bot sizga besh mahal namoz vaqtlarini eslatib turadi.\n\n'
        'Bot sizning joylashuvingizni aniqlab, vaqt mintaqangizga asoslangan holda namoz vaqtlarini ko\'rsatadi.\n\n'
        'Namoz vaqtlarini eslatmalarini olishni boshlash uchun botni ishga tushirib, joylashuvga kirish huquqini bering.\n\n'
        'Shuningdek ushbu bot sizga suralay yotlashga yordam beradi yani sizga suralar toplamini oyatlarga bolgan holida arab va lotin yozuvida oqish uchun taqdim etadi\n'
        '--------------------------------------------\n'
        "This bot will remind you of the five daily prayer times.\n\nThe bot will determine your location and display prayer times based on your time zone.\n\nTo start receiving prayer time reminders, activate the bot and grant location access.\n\nAdditionally, this bot will assist you with reading surahs. It will provide you with a collection of surahs, with verses in both Arabic and English script for you to read.",
        reply_markup=start_kb()
    )

@router.message(Command(commands='source'))
async def source(message: Message):
    await message.answer(
        text='Namoz vahtlari Aladhan Prayer (aladhan.com) saytidan olinadi.\n'
        'Suralar Al Quran (alquran.cloud) saytdian olinadi.\n'
        '--------------------------------------------\n'
        "Prayer times are taken from the Aladhan Prayer (aladhan.com) website.\n" "Surahs are taken from the Al Quran (alquran.cloud) website.",
        reply_markup=start_kb()
    )