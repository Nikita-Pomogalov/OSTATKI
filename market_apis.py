import requests
import json
import os
from datetime import datetime

# # Файл для логов
# LOG_FILE = "MarketplaceApiLog.txt"
#
#
# def log_to_file(text):
#     """Запись логов в файл"""
#     try:
#         with open(LOG_FILE, "a", encoding="utf-8") as f:
#             f.write(f"{text}\n{'-' * 50}\n")
#     except Exception as e:
#         print(f"Ошибка записи лога: {e}")


class StockRow:
    """Модель товара"""

    def __init__(self, offer_id, available=0, reserved=0):
        self.offer_id = offer_id
        self.available = available
        self.reserved = reserved


class YandexMarketAPI:
    """API для Яндекс Маркета"""

    def __init__(self, campaign_id, api_key):
        self.campaign_id = campaign_id
        self.api_key = api_key
        self.base_url = "https://api.partner.market.yandex.ru"

    async def get_stocks(self):
        """Получение остатков"""
        if not self.campaign_id or not self.api_key:
            # log_to_file("Ошибка Яндекса: Campaign ID или API Key не указан")
            return []

        # log_to_file(f"Яндекс → Campaign ID: {self.campaign_id}")

        url = f"{self.base_url}/v2/campaigns/{self.campaign_id}/offers/stocks"
        headers = {"Api-Key": self.api_key, "Content-Type": "application/json"}

        all_stocks = {}
        page_token = None
        page = 1

        try:
            while True:
                body = {"limit": 500}
                if page_token:
                    body["pageToken"] = page_token

                response = requests.post(url, headers=headers, json=body)
                # log_to_file(f"Яндекс страница {page}: статус {response.status_code}")

                if response.status_code != 200:
                    # log_to_file(f"Ошибка Яндекса: {response.text}")
                    break

                data = response.json()
                warehouses = data.get("result", {}).get("warehouses", [])

                for warehouse in warehouses:
                    offers = warehouse.get("offers", [])
                    for offer in offers:
                        offer_id = offer.get("offerId", "")
                        if not offer_id:
                            continue

                        available = 0
                        reserved = 0
                        stocks = offer.get("stocks", [])

                        for stock in stocks:
                            stock_type = stock.get("type", "").upper()
                            count = stock.get("count", 0)

                            if stock_type == "AVAILABLE":
                                available += count
                            elif stock_type in ["RESERVED", "RESERVE", "FREEZE"]:
                                reserved += count

                        if offer_id in all_stocks:
                            all_stocks[offer_id].available += available
                            all_stocks[offer_id].reserved += reserved
                        else:
                            all_stocks[offer_id] = StockRow(offer_id, available, reserved)

                page_token = data.get("result", {}).get("paging", {}).get("nextPageToken")
                page += 1

                if not page_token:
                    break

        except Exception as e:
            print(f"Ошибка Яндекса: {e}")
            # log_to_file(f"Ошибка Яндекса: {e}")

        result = sorted(all_stocks.values(), key=lambda x: x.offer_id)
        # log_to_file(f"Яндекс: загружено {len(result)} товаров")
        return result


class OzonAPI:
    """API для Ozon"""

    def __init__(self, client_id, api_key):
        self.client_id = client_id
        self.api_key = api_key
        self.base_url = "https://api-seller.ozon.ru"

    async def get_stocks(self):
        """Получение остатков"""
        url = f"{self.base_url}/v4/product/info/stocks"
        headers = {
            "Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        body = {"limit": 1000, "filter": {}}

        try:
            response = requests.post(url, headers=headers, json=body)
            # log_to_file(f"Ozon: статус {response.status_code}")

            if response.status_code != 200:
                # log_to_file(f"Ошибка Ozon: {response.text}")
                return []

            data = response.json()
            result = []

            items = data.get("items", [])
            # log_to_file(f"Ozon: найдено {len(items)} товаров")

            for item in items:
                offer_id = item.get("offer_id") or item.get("offerId", "")
                available = 0
                reserved = 0

                stocks = item.get("stocks", [])
                for stock in stocks:
                    available += stock.get("present", 0)
                    reserved += stock.get("reserved", 0)

                result.append(StockRow(offer_id, available, reserved))

            return sorted(result, key=lambda x: x.offer_id)

        except Exception as e:
            # log_to_file(f"Ошибка Ozon: {e}")
            return []


class WildberriesAPI:
    """API для Wildberries"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://seller-analytics-api.wildberries.ru"

        self.nm_to_article = {
            868320440: "BAZ-30-20-35",
            596805663: "BAZ-180-10-35",
            596662410: "BAZ-60-10-35",
            596791842: "BAZ-120-10-50",
            596849403: "BAZ-240-10-50",
            596855221: "BAZ-320-10-50",
            596841497: "BAZ-180-10-50",
            596700618: "BAZ-60-20-35",
            596745106: "BAZ-120-10-35",
            596712248: "BAZ-90-10-35",
        }

    async def get_stocks(self):
        """Получение остатков"""
        url = f"{self.base_url}/api/analytics/v1/stocks-report/wb-warehouses"
        headers = {"Authorization": self.api_key}
        body = {"limit": 1000, "offset": 0}

        try:
            response = requests.post(url, headers=headers, json=body)
            # log_to_file(f"WB: статус {response.status_code}")

            if response.status_code == 429:
                # log_to_file("WB: Слишком много запросов")
                rate_headers = {}
                for key in ['X-Ratelimit-Retry', 'X-Ratelimit-Limit', 'X-Ratelimit-Reset', 'Retry-After']:
                    if key in response.headers:
                        rate_headers[key] = response.headers[key]
                if rate_headers:
                    msg = f"WB Rate Limit заголовки: {rate_headers}"
                else:
                    msg = "WB Rate Limit заголовки не найдены"
                print(msg)
                # log_to_file(msg)
                return None

            if response.status_code != 200:
                # log_to_file(f"Ошибка WB: {response.text}")
                return []

            data = response.json()
            result = []

            items = data.get("data", {}).get("items", []) or data.get("items", [])

            for item in items:
                nm_id = item.get("nmId", 0)
                offer_id = self.nm_to_article.get(nm_id, f"nm{nm_id}")

                available = item.get("quantity", 0) or item.get("freeToSell", 0) or item.get("stock", 0)
                reserved = (item.get("reserved", 0) or 0) + (item.get("inWayToClient", 0) or 0) + (
                        item.get("inWayFromClient", 0) or 0)

                existing = next((s for s in result if s.offer_id == offer_id), None)
                if existing:
                    existing.available += available
                    existing.reserved += reserved
                else:
                    result.append(StockRow(offer_id, available, reserved))

            # log_to_file(f"WB: обработано {len(result)} уникальных товаров")
            return sorted(result, key=lambda x: x.offer_id)

        except Exception as e:
            # log_to_file(f"Ошибка WB: {e}")
            return []