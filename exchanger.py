from Bot_init import types, FSMContext, dp, EXCHANGE_API_KEY, requests, StatesGroup, State


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


# Обработка получения объема валюты для конвертации
@dp.message_handler(state=CurrencyForm.amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
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
    except ValueError:
        await message.reply("Вы ввели не число. Попробуйте еще раз.")
    await state.finish()


# Конвертация валюты
async def convert_currency(currency_from: str, currency_to: str, amount: float) -> str:
    url = f"https://api.apilayer.com/exchangerates_data/convert?from={currency_from}&to={currency_to}&amount={amount}"
    headers = {"apikey": EXCHANGE_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    data = response.json()
    converted_amount = data['result']
    return f"{amount} {currency_from} = {converted_amount} {currency_to}"
