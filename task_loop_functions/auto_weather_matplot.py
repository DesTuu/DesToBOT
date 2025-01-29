import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import io


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

    min_c_list = []
    max_c_list = []
    days_list = []

    for i in range(20):
        min_c_list.append(int(min_c[i].text.replace("°C", "").strip()))
        max_c_list.append(int(max_c[i].text.replace("°C", "").strip()))
        days_list.append(date[i].text[:2])

        weather_string += (
            f"{str(day_of_week[i].text)[:3].center(5)}│"
            f"{date[i].text.center(5)}│"
            f"{f'{min_c[i].text} do {max_c[i].text}'.center(15)}│"
            f"{cloudy[i].text.center(4)}│"
            f"{rain[i].text.center(6)}\n"
        )

    weather_string += "```"

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(days_list, min_c_list, label="min C", color='blue')
    ax.plot(days_list, max_c_list, label="max C", color='red')


    ax.set_title("Wykres temperatur w moim mieście")
    ax.set_xlabel("Dzień danego miesiąca")
    ax.set_ylabel("Temperatura °C")
    ax.axhline(0, color='black', linestyle='--', linewidth=1.5)
    ax.grid(True)
    ax.legend()

    io_temp_file = io.BytesIO()
    fig.savefig(io_temp_file, format='png', dpi=300)
    io_temp_file.seek(0)
    plt.close()

    return weather_string[:2000], io_temp_file

