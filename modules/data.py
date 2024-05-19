import os
import json

from modules.config import Vars
from modules.rate_parser import get_rate


class Data:
    def __init__(self):
        self.data_file = os.path.join(Vars.base_dir, 'data.json')
        with open(self.data_file) as file:
            self.data = json.load(file)

    def update(self):
        with open(self.data_file, 'w') as file:
            json.dump(self.data, file)

    @property
    def rate(self):
        return self.data['rate']

    def set_rate(self, rate: float):
        try:
            rate = float(rate)
        except Exception:
            return None
        lowest_rate_possible = get_rate('CNY')
        if rate >= lowest_rate_possible:
            self.data['rate'] = rate
        else:
            self.data['rate'] = lowest_rate_possible
        self.update()

    @property
    def fee(self):
        return self.data['fee']

    def set_fee(self, fee: float):
        try:
            rate = float(fee)
        except Exception:
            return None
        if rate >= 0:
            self.data['fee'] = fee
            self.update()
