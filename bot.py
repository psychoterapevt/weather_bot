import telebot
import requests
from datetime import datetime

BOT_TOKEN = '8986079087:AAGKz_xbi7TUkq-ob7vd8rNBps25_CNsAm4'
WEATHER_API_KEY = '2dc867c56d186c5c35dde2ce42c54dab'

bot = telebot.TeleBot(BOT_TOKEN)

# ПУТЬ К КАРТИНКЕ
CUSTOM_IMAGE_PATH = r'CUSTOM_IMAGE_PATH = 'logo.jpg''  # или .jpg

CITY_TRANSLATE = {
    'астана': 'Astana',
    'алматы': 'Almaty',
    'караганда': 'Karaganda',
    'актобе': 'Aktobe',
    'усть-каменогорск': 'Ust-Kamenogorsk',
    'павлодар': 'Pavlodar',
    'москва': 'Moscow',
    'спб': 'Saint Petersburg',
    'санкт-петербург': 'Saint Petersburg',
    'новосибирск': 'Novosibirsk',
    'екатеринбург': 'Yekaterinburg',
    'казань': 'Kazan',
    'нижний новгород': 'Nizhny Novgorod',
    'краснодар': 'Krasnodar',
    'сочи': 'Sochi',
    'киев': 'Kyiv',
    'львов': 'Lviv',
    'одесса': 'Odesa',
    'харьков': 'Kharkiv',
    'минск': 'Minsk',
    'гомель': 'Gomel',
    'ташкент': 'Tashkent',
    'самарканд': 'Samarkand',
    'бишкек': 'Bishkek',
    'ош': 'Osh',
    'баку': 'Baku',
    'ганжа': 'Ganja',
    'нью-йорк': 'New York',
    'нью йорк': 'New York',
    'new york': 'New York',
    'вашингтон': 'Washington',
    'чикаго': 'Chicago',
    'лос-анджелес': 'Los Angeles',
    'ла': 'Los Angeles',
    'сан-франциско': 'San Francisco',
    'лондон': 'London',
    'париж': 'Paris',
    'берлин': 'Berlin',
    'рим': 'Rome',
    'мадрид': 'Madrid',
    'прага': 'Prague',
    'варшава': 'Warsaw',
    'будапешт': 'Budapest',
    'венгрия': 'Budapest',
    'амстердам': 'Amsterdam',
    'венгра': 'Vienna',
    'дубай': 'Dubai',
    'токио': 'Tokyo',
    'пекин': 'Beijing',
    'сеул': 'Seoul',
    'сингапур': 'Singapore',
    'дели': 'Delhi',
    'мумбай': 'Mumbai',
    'сидней': 'Sydney',
    'мельбурн': 'Melbourne',
    'рио-де-жанейро': 'Rio de Janeiro',
    'буэнос-айрес': 'Buenos Aires',
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        '🌤 Привет! Я бот о погоде.\n'
        'Напиши город в формате:\n'
        'погода Алматы\n\n'
        'Доступная информация:\n'
        '🌡 Температура (средняя за день)\n'
        '💧 Влажность\n'
        '💨 Скорость ветра\n'
        '🌅 Рассвет / закат (время)\n'
        '📈 Давление'
    )

@bot.message_handler(func=lambda msg: msg.text.lower().startswith('погода'))
def get_weather(message):
    city = message.text[7:].strip()
    if not city:
        bot.reply_to(message, '❌ Напиши город после слова "погода".\nПример: погода Алматы')
        return

    city_lower = city.lower()
    city_eng = CITY_TRANSLATE.get(city_lower, city_lower)

    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city_eng}&appid={WEATHER_API_KEY}&units=metric&lang=ru'
    response = requests.get(url)

    if response.status_code != 200:
        bot.reply_to(message, f'❌ Город "{city}" не найден.\nПопробуй на английском: погода New York')
        return

    data = response.json()

    # Координаты для рассвета/заката
    city_lat = data['city']['coord']['lat']
    city_lon = data['city']['coord']['lon']

    sun_url = f'https://api.openweathermap.org/data/2.5/weather?lat={city_lat}&lon={city_lon}&appid={WEATHER_API_KEY}&units=metric&lang=ru'
    sun_response = requests.get(sun_url)
    sun_data = sun_response.json()

    # Группировка по дням
    days = {}
    for item in data['list']:
        date_obj = datetime.fromtimestamp(item['dt'])
        date_key = date_obj.strftime('%A, %d.%m')
        if date_key not in days:
            days[date_key] = []
        days[date_key].append(item)

    # Формировка текста
    reply = f'🌤 Прогноз погоды в {city.capitalize()} на неделю:\n\n'
    count = 0
    for date, items in days.items():
        if count >= 7:
            break

        temps = [i['main']['temp'] for i in items]
        avg_temp = round(sum(temps) / len(temps), 1)
        desc = items[0]['weather'][0]['description']
        humidity = round(sum(i['main']['humidity'] for i in items) / len(items))
        wind_speed = round(sum(i['wind']['speed'] for i in items) / len(items), 1)
        pressure = round(sum(i['main']['pressure'] for i in items) / len(items) * 0.750062)

        reply += f'📅 **{date}**\n'
        reply += f'   🌡 {avg_temp}°C, {desc}\n'
        reply += f'   💧 Влажность: {humidity}%\n'
        reply += f'   💨 Ветер: {wind_speed} м/с\n'
        reply += f'   📈 Давление: {pressure} мм рт. ст.\n\n'
        count += 1

    # Рассвет и закат
    if sun_response.status_code == 200 and 'sys' in sun_data:
        sunrise_ts = sun_data['sys']['sunrise']
        sunset_ts = sun_data['sys']['sunset']
        sunrise = datetime.fromtimestamp(sunrise_ts).strftime('%H:%M')
        sunset = datetime.fromtimestamp(sunset_ts).strftime('%H:%M')
        reply += f'🌅 Рассвет: {sunrise}\n'
        reply += f'🌇 Закат: {sunset}\n'

    # --- ОТПРАВЛЯЕМ КАРТИНКУ + ТЕКСТ ---
    try:
        with open(CUSTOM_IMAGE_PATH, 'rb') as photo:
            bot.send_photo(
                message.chat.id,
                photo=photo,
                caption=reply,
                parse_mode='Markdown'
            )
    except FileNotFoundError:
        bot.reply_to(message, f'❌ Файл с картинкой "{CUSTOM_IMAGE_PATH}" не найден.\nПроверь путь и название файла.')

print('✅ Бот с твоей картинкой запущен...')
bot.polling()   
