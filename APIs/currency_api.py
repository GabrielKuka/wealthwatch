import requests
import threading, time


class CurrencyAPI:
    def __init__(self, api_key: str) -> None:
        self.__API_KEY = api_key
        self.__BASE_URL = "https://openexchangerates.org/api"
        self.__ENDPOINT = (
            f"{self.__BASE_URL}/latest.json?app_id={self.__API_KEY}"
        )
        self.__rates = self._get_exchange_rates()

        self._refresh_rates_thread = threading.Thread(target=self._refresh_exchange_rates, daemon=True)
        self._refresh_rates_thread.start()
    
    def _refresh_exchange_rates(self):
        # Refresh exchange rates every 4 hours
        while True:
            time.sleep(4 * 60 * 60)
            self.__rates = self._get_exchange_rates()
    
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

        if not self.__rates:
            raise ValueError("Failed to fetch exchange rates")

        if from_currency not in self.__rates:
            raise ValueError(f"Invalid currency code {from_currency}")

        if to_currency not in self.__rates:
            raise ValueError(f"Invalid currency code {to_currency}")

        return round((self.__rates[to_currency] / self.__rates[from_currency]) * amount, 2)
