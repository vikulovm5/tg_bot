from aiogram.utils import executor
from Bot_init import dp, types, Text
from weather import WeatherForm
from exchanger import CurrencyForm
from polls import PollForm
from get_animal import send_random_animal


# Команда /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply("Привет! Я бот, который может помочь тебе с погодой, конвертацией валют, отправкой милых "
                        "животных и созданием опросов. Что ты хочешь сделать?", reply_markup=get_menu_keyboard())


# Обработка выбора функции бота
@dp.message_handler(Text(equals=['Погода', 'Конвертер валют', 'Случайное животное', 'Создать опрос']))
async def process_menu_choice(message: types.Message):
    choice = message.text
    if choice == 'Погода':
        await WeatherForm.city.set()
        await message.reply("В каком городе ты хочешь узнать погоду?")
    elif choice == 'Конвертер валют':
        await message.reply("Какую валюту ты хочешь конвертировать? Введи трехбуквенный код, например: USD - доллар, "
                            "EUR - евро, JPY - йена, RUB - рубль, AED - дирхам")
        await CurrencyForm.currency_from.set()
    elif choice == 'Случайное животное':
        await send_random_animal(message.chat.id)
    elif choice == 'Создать опрос':
        await PollForm.question.set()
        await message.reply("Какой вопрос ты хочешь задать в опросе?")


# Получение меню
def get_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Погода"))
    keyboard.add(types.KeyboardButton("Конвертер валют"))
    keyboard.add(types.KeyboardButton("Случайное животное"))
    keyboard.add(types.KeyboardButton("Создать опрос"))
    return keyboard


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
