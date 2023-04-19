import json
import logging
import os
import random

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from dotenv import load_dotenv

# Загрузка окружения из файла .env
load_dotenv()

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('BOT_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
EXCHANGE_API_KEY = os.getenv('EXCHANGE_API_KEY')

# Инициализация бота
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация логгера
logging.basicConfig(level=logging.INFO)


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


# Форма для получения города
class WeatherForm(StatesGroup):
    city = State()


# Обработка получения города
@dp.message_handler(state=WeatherForm.city)
async def process_weather_city(message: types.Message, state: FSMContext):
    city = message.text
    weather = await get_weather(city)
    if weather is None:
        await message.reply("Не удалось получить погоду для этого города. Попробуйте еще раз.")
    else:
        await message.reply(weather)
    await state.finish()


# Форма для конвертации валюты
class CurrencyForm(StatesGroup):
    currency_from = State()
    currency_to = State()
    amount = State()


# Обработка получения валюты для конвертации
@dp.message_handler(state=CurrencyForm.currency_from)
async def process_currency_from(message: types.Message, state: FSMContext):
    currency_from = message.text
    await CurrencyForm.currency_to.set()
    await state.update_data(currency_from=currency_from)
    await message.reply("В какую валюту ты хочешь конвертировать? Введи трехбуквенный код, например: USD - доллар, "
                        "EUR - евро, JPY - йена, RUB - рубль, AED - дирхам")


# Обработка получения валюты для конвертации
@dp.message_handler(state=CurrencyForm.currency_to)
async def process_currency_to(message: types.Message, state: FSMContext):
    currency_to = message.text
    await CurrencyForm.amount.set()
    await state.update_data(currency_to=currency_to)
    await message.reply("Какой объем валюты ты хочешь конвертировать?")


# Обработка получения валюты для конвертации
@dp.message_handler(state=CurrencyForm.amount)
async def process_amount(message: types.Message, state: FSMContext):
    amount = float(message.text)
    async with state.proxy() as data:
        data['amount'] = amount
        currency_from = data.get('currency_from')
        currency_to = data.get('currency_to')
        converted = await convert_currency(currency_from, currency_to, amount)
        if converted is None:
            await message.reply("Не удалось конвертировать валюту. Попробуйте еще раз.")
        else:
            await message.reply(converted)
    await state.finish()


class PollForm(StatesGroup):
    question = State()
    options = State()


# Обработка получения вопроса для опроса
@dp.message_handler(state=PollForm.question)
async def process_poll_question(message: types.Message, state: FSMContext):
    question = message.text
    await PollForm.options.set()
    await state.update_data(question=question)
    await message.reply("Введите варианты ответа через запятую (минимум 2):")


# Обработка получения вариантов ответа для опроса
@dp.message_handler(state=PollForm.options)
async def process_poll_options(message: types.Message, state: FSMContext):
    options = message.text.split(", ")
    if len(options) < 2:
        await message.reply("Введите минимум 2 варианта ответа")
        return
    await state.update_data(options=options)
    data = await state.get_data()
    question = data.get('question')
    options = data.get('options')
    await create_poll(question, options, message.chat.id)
    await message.reply("Опрос создан!")
    await state.finish()


# Обработка команды создания опроса
@dp.message_handler(commands=['create_poll'])
async def create_poll_command(message: types.Message):
    await message.reply("Введите вопрос для опроса:")
    await PollForm.question.set()


# Получение меню
def get_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Погода"))
    keyboard.add(types.KeyboardButton("Конвертер валют"))
    keyboard.add(types.KeyboardButton("Случайное животное"))
    keyboard.add(types.KeyboardButton("Создать опрос"))
    return keyboard


# Получение погоды
async def get_weather(city: str) -> str:
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&appid={WEATHER_API_KEY}&units=metric'
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = json.loads(response.text)
    weather = data['weather'][0]['description']
    temp = data['main']['temp']
    return f"В городе {city} сейчас {weather}, температура {temp} градусов Цельсия."


# Конвертация валюты
async def convert_currency(currency_from: str, currency_to: str, amount: float) -> str:
    url = f"https://api.apilayer.com/exchangerates_data/convert?from={currency_from}&to={currency_to}&amount={amount}"
    headers = {"apikey": EXCHANGE_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    data = response.json()
    print(data)
    converted_amount = data['result']
    return f"{amount} {currency_from} = {converted_amount} {currency_to}"


# Функция для получения случайного животного
async def send_random_animal(chat_id: int):
    animal_types = ['cat', 'dog', 'fox', 'panda', 'koala', 'bird', 'raccoon', 'kangaroo']
    animal_type = random.choice(animal_types)
    response = requests.get(f"https://some-random-api.ml/img/{animal_type}")
    animal_url = response.json()['link']
    await bot.send_photo(chat_id=chat_id, photo=animal_url)


# Создание опроса
async def create_poll(question: str, options: list, chat_id: int):
    poll = await bot.send_poll(chat_id=chat_id, question=question, options=options, is_anonymous=False)
    return poll


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
