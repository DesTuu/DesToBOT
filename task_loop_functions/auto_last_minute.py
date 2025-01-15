import requests
from bs4 import BeautifulSoup


def auto_last_minute(auto_last_minute_string="Promocyjne loty z Gdańska: \n\n"):
    url = "https://www.latamy.pl/13p,promocje_bilety_lotnicze.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    data = soup.find_all('div', id='polaczenia_center')

    for i in data:
        if "Promocje z Gdańska" in i.text:
            info = i.find_all("li")
            for j in info:
                if "inne promocje" not in j.text and "Promocje z Gdańska" not in j.text:
                    auto_last_minute_string += f"- {j.text.strip()}\n"

    return auto_last_minute_string