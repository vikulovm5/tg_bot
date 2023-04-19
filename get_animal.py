import random
from Bot_init import requests, bot


# Функция для получения случайного животного
async def send_random_animal(chat_id: int):
    animal_types = ['cat', 'dog', 'fox', 'panda', 'koala', 'bird', 'raccoon', 'kangaroo']
    animal_type = random.choice(animal_types)
    response = requests.get(f"https://some-random-api.ml/img/{animal_type}")
    animal_url = response.json()['link']
    await bot.send_photo(chat_id=chat_id, photo=animal_url)
