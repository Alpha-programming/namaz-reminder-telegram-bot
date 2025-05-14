from aiogram.utils.keyboard import ReplyKeyboardBuilder

def start_kb():
    kb = ReplyKeyboardBuilder()

    kb.button(text="Shaharni tanlash(Choose a region)")
    kb.button(text="Suralar (Surahs)")

    kb.adjust(2)

    return kb.as_markup(resize_keyboard=True)