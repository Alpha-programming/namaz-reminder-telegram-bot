from aiogram import Router,F
from aiogram.types import Message
from keyboards.inline import choose_country,choose_surah

router = Router()

@router.message(F.text == "Shaharni tanlash(Choose a region)")
async def location(message: Message):
    await message.reply(text="Istiqomat qilayotgan shahringizni tanlang:(Namoz vaqtlarini aniqlash uchun)\n\nSelect your city of residence: (To determine prayer times)",
                        reply_markup=choose_country())

@router.message(F.text == 'Suralar (Surahs)')
async def sura(message: Message):
    await message.reply(text="Qur'oni Karimdagi barcha 114 surani tanlab, o‘qishingiz mumkin.\n\nYou can select and read all 114 surahs in the Holy Quran.",
                        reply_markup=choose_surah())

