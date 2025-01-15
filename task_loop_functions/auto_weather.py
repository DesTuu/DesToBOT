import requests
from bs4 import BeautifulSoup


def auto_weather():
    weather_string = "Prognoza pogody w moim mieście na najbliższe dni:\n\n"
    url = 'https://pogoda.interia.pl/prognoza-dlugoterminowa-tczew,cId,35426'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    day_of_week = soup.find_all('span', class_='day')
    date = soup.find_all('span', class_='date')
    min_c = soup.find_all('span', class_='weather-forecast-longterm-list-entry-forecast-lowtemp')
    max_c = soup.find_all('span', class_='weather-forecast-longterm-list-entry-forecast-temp')
    cloudy = soup.find_all('span', class_='weather-forecast-longterm-list-entry-cloudy-cloudy-value')
    rain = soup.find_all('span', class_='weather-forecast-longterm-list-entry-precipitation-value')

    for i in range(3):
        weather_string += f"- {str(day_of_week[i].text)[:3]} {date[i].text} " \
                          f"**od {min_c[i].text} do {max_c[i].text}** - " \
                          f"☁ {cloudy[i].text} - " \
                          f"🌧️ {rain[i].text}\n"

    return weather_string[:2000]
