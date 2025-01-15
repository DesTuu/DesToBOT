import requests
from bs4 import BeautifulSoup
import settings


def auto_bus_check_update():
    site_updated = False
    response = requests.get("https://komunikacja.tczew.pl/komunikaty.html")
    soup = BeautifulSoup(response.text, 'lxml')
    news_item = soup.find('div', class_="news_item")
    date_of_last_update = news_item.find('em')

    with open(f"{settings.DB_DIR}/date_of_last_update.txt", "r") as f:
        if date_of_last_update.text != f.read():
            site_updated = True

    if site_updated:
        with open(f"{settings.DB_DIR}/date_of_last_update.txt", "w") as f:
            f.write(date_of_last_update.text)

        title = news_item.find("h4")
        content = news_item.find("p")
        string = f"**{date_of_last_update.text} - {title.text}**\n\n{content.text}\n\n" \
                 f"https://komunikacja.tczew.pl/komunikaty.html"
        return string

    return None
