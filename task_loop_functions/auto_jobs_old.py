import requests
from bs4 import BeautifulSoup


def auto_jobs():
    url1 = "https://www.pracuj.pl/praca/python;kw/tczew;wp?rd=50"
    response1 = requests.get(url1)
    soup1 = BeautifulSoup(response1.text, 'lxml')
    content1 = soup1.find_all('div', class_="tiles_c1k2agp8")

    try:
        url2 = "https://www.pracuj.pl/praca/python;kw/tczew;wp?rd=50&pn=2"
        response2 = requests.get(url2)
        soup2 = BeautifulSoup(response2.text, 'lxml')
        content2 = soup2.find_all('div', class_="tiles_c1k2agp8")

        combined_content = content1 + content2
    except:
        combined_content = content1

    job_string = f"{url1}:\n"
    job_names_used = []
    useless_jobs = ["Analityk", "Consulting", "Artist", "3D"]

    for i in combined_content:
        job_bool = True
        job_name = i.find("h2")

        if job_name.text not in job_names_used:
            for j in useless_jobs:
                if j in job_name.text:
                    job_bool = False

            if job_bool:
                job_names_used.append(job_name.text)

                job_place = i.find("div", class_="tiles_cegq0mb")
                if "Gdańsk" in job_place.text:
                    job_place = "Gdańsk"
                elif "Gdynia" in job_place.text:
                    job_place = "Gdynia"
                else:
                    job_place = "Inne"

                job_type = i.find("ul")
                if "Junior" in job_type.text:
                    job_type = "Junior"
                elif "Mid" in job_type.text:
                    job_type = "Mid"
                else:
                    job_type = "Senior"

                if job_type != "Senior" and job_type != "Mid":
                    job_link = i.find("a").get('href')

                    job_string += f"- {job_name.text} ({job_type}) w {job_place} {job_link}\n"

    return job_string
