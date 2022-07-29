import pathlib
import shutil

import bs4
import requests

BASE_URL = 'http://www.fuelprices.gr'
DATA_PATH = pathlib.Path('../var')


def fetch_data():
    """Fetch data from the site.
    """
    for path in ('deltia_d.view', 'deltia_d.view', 'deltia_dn.view'):
        response = requests.get(f"{BASE_URL}/{path}")
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            if link.has_attr('href') and link['href'].startswith('./files'):
                file_path = DATA_PATH / link['href']
                if not file_path.exists():
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    print(f"Downloading file {link['href']}")
                    file_url = f"{BASE_URL}/{link['href']}"
                    with requests.get(file_url, stream=True) as r, file_path.open('wb') as f:
                        shutil.copyfileobj(r.raw, f)


if __name__ == '__main__':
    fetch_data()
