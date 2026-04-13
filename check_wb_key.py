import requests

# Вставьте ваш ключ сюда
API_KEY = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjYwMzAydjEiLCJ0eXAiOiJKV1QifQ.eyJhY2MiOjMsImVudCI6MSwiZXhwIjoxNzkxNjU4NTczLCJmb3IiOiJzZWxmIiwiaWQiOiIwMTlkN2I1My1hYTcwLTcyMzktYjVlNi1kMGIxZWM2NjllNTAiLCJpaWQiOjgxODkzOTEsIm9pZCI6NDM4ODgzOCwicyI6ODE2NjIsInNpZCI6IjU4NWViMzcyLTVhZWYtNDE2Zi05ZDkyLTc2NDZlNmZiNTc5OCIsInQiOmZhbHNlLCJ1aWQiOjgxODkzOTF9.4B11lMuqjHNTy0rd879nPRKCK_AxUGgHcEfqqFuv7xa4ZEwyioZVcarMkuRmXpybF2T0_XPx3bCQuaW6Yqjuug"

def test_endpoint(url, headers, description):
    print(f"\n🔍 Тестируем: {description}")
    print(f"   URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   ✅ Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📦 Данных: {len(data) if isinstance(data, list) else 'объект'}")
            return True
        elif response.status_code == 401:
            print("   ❌ Ошибка: Неверный ключ или нет прав")
        elif response.status_code == 403:
            print("   ❌ Ошибка: Доступ запрещён (не хватает прав)")
        elif response.status_code == 429:
            print("   ⚠️ Лимит запросов исчерпан (429)")
        else:
            print(f"   ⚠️ Другой статус: {response.status_code}")
        return False
    except Exception as e:
        print(f"   ❌ Ошибка подключения: {e}")
        return False

headers = {"Authorization": API_KEY}

# Тестируем разные эндпоинты
print("=" * 60)
print("АНАЛИЗ API-КЛЮЧА WILDBERRIES")
print("=" * 60)

# 1. Информация о товарах (базовый)
test_endpoint(
    "https://marketplace-api.wildberries.ru/api/v3/things",
    headers,
    "Товары (базовый доступ)"
)

# 2. Остатки (наш основной эндпоинт)
test_endpoint(
    "https://marketplace-api.wildberries.ru/api/v3/stocks",
    headers,
    "Остатки через marketplace-api"
)

# 3. Аналитика (тот, который выдаёт 429)
test_endpoint(
    "https://seller-analytics-api.wildberries.ru/api/analytics/v1/stocks-report/wb-warehouses",
    {**headers, "Content-Type": "application/json"},
    "Аналитика остатков (требует специальных прав)"
)

# 4. Информация о складах
test_endpoint(
    "https://marketplace-api.wildberries.ru/api/v3/warehouses",
    headers,
    "Склады (базовый доступ)"
)

print("\n" + "=" * 60)
print("ВЫВОД:")
print("Если статус 200 → ключ подходит для этого эндпоинта")
print("Если статус 401 или 403 → ключ не имеет прав")
print("Если статус 429 → превышен лимит (подождите 1-2 минуты)")
print("=" * 60)