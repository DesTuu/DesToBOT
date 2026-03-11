from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
import asyncio


async def auto_convents(convents_string=""):
    tuple_of_cities = ('Gdańsk', 'Gdynia', 'Sopot', 'Poznań', 'Bydgoszcz', 'Gniezno', 'Toruń')
    url = 'https://konwenty-poludniowe.pl/konwenty/kalendarz'
    session = AsyncHTMLSession()
    response = await session.get(url)
    await response.html.arender(sleep=1, keep_page=True, scrolldown=1, timeout=6000)
    soup = BeautifulSoup(response.html.html, 'lxml')

    elements = soup.select('.odd, .even')

    for element in elements:
        my_split = (element.text.split("\n"))
        for i in my_split:
            if not i or i == " " or i == "  ":
                my_split.remove(i)

        date, name, place, topic = my_split

        if place.strip() in tuple_of_cities:
            convents_string += f"- {name.strip()} ({topic.strip()}) - {place.strip()}: {date.strip()}\n"

    return convents_string
