from bs4 import BeautifulSoup
import requests


def auto_currencies():
    url = 'https://www.waluty.pl/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    currency_string = f"{str(soup.find('h2', class_='heading').text).strip()}\n"
    currency_names = soup.find_all('td', class_='font-size-large-lg')
    currency_value = soup.find_all('span', class_='arrow-xs')
    for i in range(len(currency_value)):
        cur_name = currency_names[i].text.strip()
        my_range = 5
        if "100" in cur_name:
            my_range = 7
        new_cur_name = cur_name[:my_range] + " (" + cur_name[my_range:] + ")"
        currency_string += f"- {new_cur_name} = {currency_value[i].text} zł\n"

    return currency_string
