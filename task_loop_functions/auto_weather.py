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

    weather_string += "```\n"
    weather_string += (
        f"{'Dzień'.center(5)}│{'Datum'.center(5)}│{'Temperatura'.center(15)}│"
        f"{'Chmu'.center(4)}│{'Opady'.center(6)}\n"
    )
    weather_string += "─" * (len(weather_string) - 56) + "\n"

    for i in range(20):
        weather_string += (
            f"{str(day_of_week[i].text)[:3].center(5)}│"
            f"{date[i].text.center(5)}│"
            f"{f'{min_c[i].text} do {max_c[i].text}'.center(15)}│"
            f"{cloudy[i].text.center(4)}│"
            f"{rain[i].text.center(6)}\n"
        )

    weather_string += "```"

    return weather_string[:2000]

