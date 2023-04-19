from Bot_init import dp, requests, types, FSMContext, json, WEATHER_API_KEY, StatesGroup, State


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
