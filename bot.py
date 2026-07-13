import telebot
import requests
from datetime import datetime

BOT_TOKEN = '8986079087:AAGKz_xbi7TUkq-ob7vd8rNBps25_CNsAm4'
WEATHER_API_KEY = '2dc867c56d186c5c35dde2ce42c54dab'

bot = telebot.TeleBot(BOT_TOKEN)

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
    bot.reply_to(message, '🌤 Привет! Напиши: погода Алматы')

@bot.message_handler(func=lambda msg: msg.text.lower().startswith('погода'))
def get_weather(message):
    city = message.text[7:].strip()
    if not city:
        bot.reply_to(message, 'Пример: погода Алматы')
        return

    city_eng = CITY_TRANSLATE.get(city.lower(), city)
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city_eng}&appid={WEATHER_API_KEY}&units=metric&lang=ru'
    response = requests.get(url)

    if response.status_code != 200:
        bot.reply_to(message, f'❌ Город "{city}" не найден.')
        return

    data = response.json()
    days = {}
    for item in data['list']:
        date_obj = datetime.fromtimestamp(item['dt'])
        date_key = date_obj.strftime('%A, %d.%m')
        if date_key not in days:
            days[date_key] = []
        days[date_key].append(item)

    reply = f'🌤 Прогноз в {city}:\n\n'
    count = 0
    for date, items in days.items():
        if count >= 7:
            break
        temps = [i['main']['temp'] for i in items]
        avg_temp = round(sum(temps) / len(temps), 1)
        desc = items[0]['weather'][0]['description']
        reply += f'{date}: {avg_temp}°C, {desc}\n'
        count += 1

    bot.reply_to(message, reply)

print('✅ Бот запущен...')
bot.polling()
