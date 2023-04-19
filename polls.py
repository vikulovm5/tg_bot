from Bot_init import bot, types, FSMContext, dp, StatesGroup, State


# Форма получения опроса
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


# Создание опроса
async def create_poll(question: str, options: list, chat_id: int):
    poll = await bot.send_poll(chat_id=chat_id, question=question, options=options, is_anonymous=False)
    return poll
