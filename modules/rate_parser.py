import requests
from bs4 import BeautifulSoup


def parse_rates():
    base_url = 'https://www.cbr.ru/currency_base/daily/'

    response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', attrs={'class': 'data'})
        if table:
            currencies = []
            rates = {}
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                currency = cells[1].text
                rate_raw = cells[4].text
                rate_raw = rate_raw.replace(',', '.')
                rate = float(rate_raw)
                currencies.append(currency)
                rates[currency] = rate
            return currencies, rates
        else:
            return None, None
    else:
        return response.status_code, None


def get_rate(currency):
    currencies, rates = parse_rates()
    selected_currency = currency
    if selected_currency in currencies:
        return rates[selected_currency]
    else:
        return None
