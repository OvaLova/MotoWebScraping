import datetime
import re
import time
import requests
import schedule
from bs4 import BeautifulSoup
import csv

BASE_URLS = ['https://www.motomus.ro/', 'https://motorteam.ro/',
             'https://www.asfalt-uscat.ro/', 'https://www.bikermag.ro/']
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                  'Version/17.3.1 Safari/605.1.15'
}
ARTICLES = []
CATEGORIES = {
    'https://www.motomus.ro/': ['integrale', 'geaca', 'manusi'],
    'https://motorteam.ro/': ['integrale', 'geci-moto', 'manusi'],
    'https://www.asfalt-uscat.ro/': ['integrale', 'geci-123', 'geci-de-piele', 'manusi-moto'],
    'https://www.bikermag.ro/': ['casti-moto-integrale', 'geci-moto', 'manusi-protectie-moto-din-piele', 'manusi-protectie-moto-din-textil']
}
PATH = '/Users/ovidiucandea/Desktop/MOTO/'


class Scraper:
    def __init__(self, clock, base_url, complement):
        self.session = requests.session()
        self.headers = HEADERS
        self.base_url = base_url
        self.complement = complement
        self.time = clock

    def extract(self):
        page = 0
        last_page = None
        while True:
            url = self.base_url + str(self.complement)
            try:
                if page != 0:
                    url = f'{url}?p={page}'
                else:
                    pass
                response = self.session.get(url, headers=self.headers).content
                soup = BeautifulSoup(response, 'html.parser')
                target = None
                match self.base_url:
                    case 'https://www.motomus.ro/' | 'https://motorteam.ro/' | 'https://www.asfalt-uscat.ro/' | 'https://www.bikermag.ro/':
                        target = soup.find('div', class_='product-listing clearfix')
                    case _:
                        pass
                if page == 0:
                    target_pages = None
                    match self.base_url:
                        case 'https://www.motomus.ro/' | 'https://motorteam.ro/' | 'https://www.asfalt-uscat.ro/' | 'https://www.bikermag.ro/':
                            target_pages = target.find('div', class_=lambda value: value and value.startswith(
                                'pagination pg-categ'))
                            target_pages = target_pages.find('ol', class_='fr').find_all('a')
                        case _:
                            pass
                    pages = []
                    for i in target_pages:
                        try:
                            pages.append(int(i.get_text()))
                        except ValueError:
                            continue
                    last_page = max(pages)
                else:
                    pass
                nr = 0
                match self.base_url:
                    case 'https://www.motomus.ro/' | 'https://motorteam.ro/' | 'https://www.asfalt-uscat.ro/' | 'https://www.bikermag.ro/':
                        target_products = target.find('div', class_='row product')
                        products = target_products.find_all('div', class_=lambda value: value and value.startswith(
                         'product-box center col-md-'))
                        for product in products:
                            nr += 1
                            product_id = product.get('data-product-id')
                            details = product.find('div', class_='top-side-box')
                            link = details.a.get('href')
                            name = details.a.get_text()
                            price = details.find(name='span', class_=lambda value: value and value.startswith(
                                'text-main -g-product-box-final-price-')).get_text().strip('\n').strip('\t')
                            dictionary = {
                                'Product ID': product_id,
                                'Name': name,
                                f'Price RON ({self.time})': make_int(price),
                                'Link': link
                            }
                            ARTICLES.append(dictionary)
                    case _:
                        pass
                print(f'On page {page}, url {url}, there were {nr} {self.complement}')
                print(f'Finished extracting page {page} of {self.complement}')
                page += 1
                if page >= last_page:
                    # print(f'Last {self.complement} (on last page) is {dictionary}')
                    break
            except Exception as error:
                print(f'!!!{error}!!!')
                break
        print(f'{len(ARTICLES)} {self.complement} were gathered')
        return


def main():
    global ARTICLES
    clock = str(datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S'))
    for site in BASE_URLS:
        for complement in CATEGORIES[site]:
            moto = Scraper(clock, site, complement)
            moto.extract()
        file_name = f"{site.lstrip('https://www.').rstrip('.ro/')}.csv"
        file_path = f'{PATH}MotoGearMonitor_{file_name}'
        with open(file_path, 'a', newline='') as file:
            if file.tell() == 0:
                empty = True
            else:
                empty = False
            print(f'{file_name} is empty? {empty}')
            file.close()
        if empty:
            with open(f"{PATH}MotoGearMonitor_{site.lstrip('https://www.').rstrip('.ro/')}"
                      f'.csv', 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['Product ID', 'Name', 'Link', 'Tracked', f'Price RON ({clock})'])
                writer.writeheader()
                writer.writerows(ARTICLES)
                ARTICLES = []
                file.close()
        else:
            with open(f"{PATH}MotoGearMonitor_{site.lstrip('https://www.').rstrip('.ro/')}"
                      f'.csv', 'r') as file:
                reader = csv.reader(file)
                data = list(reader)
                headers = data[0]
                index_track = headers.index('Tracked')
                index_id = headers.index('Product ID')
                index_name = headers.index('Name')
                new_prices = []
                name_ids = []
                for article in ARTICLES:
                    name_id = article['Product ID']
                    new_price = article[f'Price RON ({clock})']
                    new_prices.append(new_price)
                    name_ids.append(name_id)
                data[0].append(f'Price RON ({clock})')
                for i in range(1, len(data)):
                    if data[i][index_track] == 'Yes':
                        x = 0
                        while x <= len(ARTICLES)*1.3:
                            try:
                                if data[i][index_id] == name_ids[i-1-x]:
                                    data[i].append(new_prices[i-1-x])
                                    break
                                elif data[i][index_id] == name_ids[i-1+x]:
                                    data[i].append(new_prices[i-1+x])
                                    break
                                else:
                                    print('Site listing order changed')
                                    x += 1
                            except IndexError:
                                print(f'Article {data[i][index_id]}({data[i][index_name]}) no longer found')
                                data[i].append('---')
                                break
                    else:
                        data[i].append('')
                file.close()
            with open(f"{PATH}MotoGearMonitor_{site.lstrip('https://www.').rstrip('.ro/')}"
                      f'.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)
                ARTICLES = []
                file.close()
    print('Process finished')


def make_int(price_str):
    price_int = float(re.sub('[A-Za-z.\n ]', '', price_str).replace(',', '.'))
    return price_int


schedule.every().day.at("12:00").do(main)
while True:
    schedule.run_pending()
    time.sleep(1)

# if __name__ == '__main__':
#     main()
