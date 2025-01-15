import requests
from bs4 import BeautifulSoup


def auto_concerts(concerts_string=""):
    url = 'https://rytmy.pl/hip-hop-rap/gdansk/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    try:
        next_page_link = soup.find('a', class_='next page-numbers')['href']

        response_next_page = requests.get(next_page_link)
        soup_next_page = BeautifulSoup(response_next_page.text, 'lxml')

        combined_soup = soup.find_all('div', class_='eventsItemWrapper') + soup_next_page.find_all(
            'div',
            class_='eventsItemWrapper')

    except Exception as e:
        combined_soup = soup.find_all('div', class_='eventsItemWrapper')

    for event in combined_soup:
        date = event.find('meta', itemprop='startDate')['content']
        title = event.find('h2', itemprop='name').text
        location = event.find('strong').text.strip()

        concerts_string += f"- {title} {location} {date}\n"

    lines = concerts_string.split('\n')
    unique_lines = []
    for line in lines:
        if line not in unique_lines:
            unique_lines.append(line)

    return '\n'.join(unique_lines)
