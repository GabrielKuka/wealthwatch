import requests
from cachetools import TTLCache, cached


class CurrencyAPI:
    def __init__(self, api_key: str) -> None:
        self.__API_KEY = api_key
        self.__BASE_URL = "https://openexchangerates.org/api"
        self.__ENDPOINT = (
            f"{self.__BASE_URL}/latest.json?app_id={self.__API_KEY}"
        )

    @cached(cache=TTLCache(maxsize=1, ttl=(60 * 60 * 4)))
    def _get_exchange_rates(self):
        try:
            response = requests.get(self.__ENDPOINT)
            response.raise_for_status()
            return response.json()["rates"]
        except requests.exceptions.HTTPError as err:
            print(str(err))
            return {}

    def convert(
        self, from_currency: str, to_currency: str, amount: float
    ) -> float:
        if from_currency == to_currency:
            return amount

        rates = self._get_exchange_rates()
        if not rates:
            raise ValueError("Failed to fetch exchange rates")

        if from_currency not in rates:
            raise ValueError(f"Invalid currency code {from_currency}")

        if to_currency not in rates:
            raise ValueError(f"Invalid currency code {to_currency}")

        return round((rates[to_currency] / rates[from_currency]) * amount, 2)
