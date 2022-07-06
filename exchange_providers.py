from abc import ABC, abstractmethod
import requests
import json
import logging

log = logging.getLogger(__name__)

class ExchangeProvider(ABC):
    @abstractmethod
    def get_rate() -> None:
        pass

class ExchangerateProvider(ExchangeProvider):
    def __init__(self,_from: str, to: str, amount: int) -> None:
        self.name = 'Exchangerate'
        self._from = _from
        self.to = to
        self.amount = amount
        self.url = f'https://api.exchangerate-api.com/v4/latest/{self._from}'
        self.rates = dict()

    def __gt__(self, other):
        return self.rates.get(self.to) > other.rates.get(self.to)

    def _parse_result(self, results: dict) -> float:
        rates = results.get('rates')
        if not rates:
            raise Exception('Bad response from server')
        result = rates.get(self.to, 0)
        self.rates[self.to] = result
        return result

    def get_rate(self) -> None:
        try: 
            resp = requests.get(self.url)
            j = json.loads(resp.content)
            result = self._parse_result(j)
            result_amount = result * float(self.amount)
            log.info(f'amount of {self.amount} FROM exRate: {result} => {result_amount}')
            self.amount = int(result_amount)
        except Exception as e:
            log.error(f'Error: {e}')


class FrankfurterProvider(ExchangeProvider):
    def __init__(self,_from: str, to: str, amount: int) -> None:
        self.name = 'Frankfurter'
        self._from = _from
        self.to = to
        self.amount = amount
        self.url = f'https://api.frankfurter.app/latest?from={self._from}&to={self.to}'
        self.rates = dict()

    def _parse_result(self, results: dict) -> float:
        rates = results.get('rates')
        if not rates:
            raise Exception('Bad response from server')
        self.rates[self.to] = rates.get(self.to, 0)
        return self.rates[self.to]

    def __gt__(self, other):
        return self.rates.get(self.to) > other.rates.get(self.to)
    
    def get_rate(self) -> None:
        try: 
            resp = requests.get(self.url)
            j = json.loads(resp.content) 
            result = self._parse_result(j)
            result_amount = result * float(self.amount)
            log.info(f'Amount of {self.amount} FROM frank: {result} => {result_amount}')
            self.amount = int(result_amount)
        except Exception as e:
            log.error(f'Error: {e}')
