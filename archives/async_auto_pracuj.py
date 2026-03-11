import asyncio
import aiohttp
from bs4 import BeautifulSoup


async def fetcher(session: aiohttp.ClientSession, url: str):
    try:
        async with session.get(url) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "lxml")
            content1 = soup.find_all(class_="gp-pp-reset type--positioned tiles_b18pwp01 core_po9665q")
            content2 = soup.find_all(class_="gp-pp-reset tiles_b18pwp01 core_po9665q")

            junior_jobs = set()
            useless_jobs = ["Consulting", "Artist", "3D", "Menedżer", "Business", "Wdrożeniowiec", "Lead",
                            "Cyber", "Operator", "German", "Manager"]

            for i in (content1 + content2):
                level = i.find(class_="mobile-hidden tiles_i14a41ct")
                name = i.find(class_="tiles_h1p4o5k6")
                link_content = i.find(class_="tiles_cnb3rfy core_n194fgoq")

                if level and name and link_content:
                    level_text = level.text.strip()
                    name_text = name.text.strip()
                    link = link_content.get("href").strip()

                    if "senior" not in level_text.lower() and "mid" not in level_text.lower() and not any(job in name_text for job in useless_jobs):
                        junior_jobs.add(f"- {link}")


            return "\n".join(junior_jobs)
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return ""


async def async_auto_pracuj():
    async with aiohttp.ClientSession() as session:
        urls = [f"https://it.pracuj.pl/praca/python;kw/tczew;wp?rd=70&pn={i}&iwhpl=true" for i in range(1, 6)]
        tasks = [fetcher(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return "- https://it.pracuj.pl/praca/python;kw/tczew;wp?rd=100&iwhpl=true \n" + "\n".join(results)
