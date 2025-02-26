from bs4 import BeautifulSoup
import requests
import json
import matplotlib.pyplot as plt
import io
import settings


def get_currency_data():
    try:
        with open(f"{settings.DB_DIR}/currencies.json", 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading currency data: {e}")
        return [], [], [], []

    gbp = data.get('gbp', [])
    eur = data.get('eur', [])
    usd = data.get('usd', [])
    date = data.get('date', [])

    return gbp, eur, usd, date


def save_currency_data(gbp, eur, usd, date):
    data = {
        "gbp": gbp,
        "eur": eur,
        "usd": usd,
        "date": date
    }

    with open(f"{settings.DB_DIR}/currencies.json", 'w') as file:
        json.dump(data, file, indent=4)


def auto_currencies():
    url = 'https://www.waluty.pl/'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        currency_string = f"{str(soup.find('h2', class_='heading').text).strip()}\n"
        single_date = soup.find('h2', class_='heading').text.strip().split()[-1]
        single_date = single_date[:5]
        currency_names = soup.find_all('td', class_='font-size-large-lg')
        currency_value = soup.find_all('span', class_='arrow-xs')
        for i in range(len(currency_value)):
            cur_name = currency_names[i].text.strip()
            my_range = 5
            if "100" in cur_name:
                my_range = 7
            new_cur_name = cur_name[:my_range] + " (" + cur_name[my_range:] + ")"
            currency_string += f"- {new_cur_name} = {currency_value[i].text} zł\n"

            # get new single data
            if "gbp" in new_cur_name.lower():
                single_gbp = currency_value[i].text
            if "eur" in new_cur_name.lower():
                single_eur = currency_value[i].text
            if "usd" in new_cur_name.lower():
                single_usd = currency_value[i].text

        # make lists
        gbp, eur, usd, date = get_currency_data()

        if single_date not in date:
            date.append(single_date)
            gbp.append(float(single_gbp.replace(',', '.')))
            eur.append(float(single_eur.replace(',', '.')))
            usd.append(float(single_usd.replace(',', '.')))

        if len(date) > 10:
            save_currency_data(gbp[1:], eur[1:], usd[1:], date[1:])
        else:
            save_currency_data(gbp, eur, usd, date)

        # plot
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(date, gbp, color='#32CD32', label="Funt [GBP]")
        ax.plot(date, eur, color='#1E90FF', label="Euro [EUR]")
        ax.plot(date, usd, color='#8A2BE2', label="Dolar [USD]")

        ax.set_title("Wykres walut w ostatnim czasie")
        ax.set_xlabel("Data")
        ax.set_ylabel("PLN za 1")
        ax.grid(linestyle="--")
        ax.legend()

        # io
        io_temp_file = io.BytesIO()
        fig.savefig(io_temp_file, format='png', dpi=300)
        io_temp_file.seek(0)

        plt.clf()
        plt.close(fig)

        return currency_string, io_temp_file

    else:
        return f"response.status_code == {response.status_code}"