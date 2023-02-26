import requests

city = "Moscow, RU"
appid = "06bb2e12a854322c95aca62be6cef2a2"

res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                   params={'q': city, 'units': 'metric', 'lang': 'ru', 'APPID': appid})

data = res.json()
print("Прогноз погоды на неделю:")
for i in data['list']:
    print("Дата <", i['dt_txt'], "> \r\nТемпература <",
          '{0:+3.0f}'.format(i['main']['temp']), "> \r\nПогодные условия <", i['weather'][0]['description'],
          "> \r\nСкорость ветра <", i['wind']['speed'], "> \r\nВидимость <", i['visibility'], ">")
    print("____________________________")
