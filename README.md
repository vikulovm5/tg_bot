# Что это, и для чего нужно
#### Это бот, который может:
1. Сообщить погоду в выбранном городе.
2. Конвертировать валюту.
3. Загрузить картинку с рандомным животным.
4. Создать опрос в диалоге.

# Требования
1. Для работы бота, у вас должен быть установлен интерпретатор для python.
2. На системе в которой запускается бот, должен быть доступ к Telegram.

# Установка
Для начала вам нужен сам бот в телеграме, а точнее **\<token\>** бота. Надеюсь вы уже знаете где и как его получить. Если нет - [вам сюда](https://core.telegram.org/bots)

Если у вас есть **\<token\>** бота, тогда понадобится еще **access_token** с api для [конвертера валют](https://apilayer.com/marketplace/exchangerates_data-api?utm_source=apilayermarketplace&utm_medium=featured), а так же **access_token** для api [погоды](https://home.openweathermap.org/)

У вас есть 3 токена? Хорошо, скачивайте бота:
```
git clone 
```
Войдите в папку с ботом:
```
cd tg_bot
```
Создайте виртуальное окружение и активируйте его:
```
python3 -m venv env
source env/bin/activate
```
Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
Почти готово!
Далее откройте файл .env, и измените 3 строчки конфигурации:
```
BOT_TOKEN=токен тг бота
WEATHER_API_KEY=токен api погоды
EXCHANGE_API_KEY=токен api обмена валюты
```

И всё, ваш бот готов к использованию. Запускаем:
```
python main.py
```

# Как управлять?
Для начала можете отправить боту команду **"/start"**, чтобы бот создал клавиатуру с основными командами, но это не обязательно.

#### Команды, которые понимает бот:
1. Вышеупомянутый **"/start"**
1. **"Погода"** - Показывает погоду в выбранном городе
1. **"Конвертер валют"** - Конвертировать определенный объем валюты в другую
1. **"Случайное животное"** - Получить фотографию рандомного животного
1. **"Создать опрос"** - Создать опрос в чате, с выбранным количеством вариантов
