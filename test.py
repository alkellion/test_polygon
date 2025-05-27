import os
import requests
from time import sleep

from dotenv import load_dotenv

load_dotenv()

POLYGONSCAN_API_KEY = os.getenv("POLYGONSCAN_API_KEY")  # Ваш ключ
TOKEN_ADDRESS = os.getenv("TOKEN_ADDRESS")  # Адрес токена в нижнем регистре

BASE_URL = "https://api.polygonscan.com/api"


def get_transfer_events(token_address, start_block=0, end_block=99999999, page=1, offset=10):
    """Получаем события Transfer токена с PolygonScan"""
    params = {
        "module": "logs",
        "action": "getLogs",
        "fromBlock": start_block,
        "toBlock": end_block,
        "address": token_address,
        "topic0": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",  # Keccak256 Transfer(address,address,uint256)
        "page": page,
        "offset": offset,
        "apikey": POLYGONSCAN_API_KEY,
    }
    response = requests.get(BASE_URL, params=params)

    data = response.json()
    if data["status"] == "1":
        return data["result"]
    else:
        print(f"Ошибка получения событий: {data['message']}")
        return []


def get_balance(address, token_address):
    """Получаем баланс токена у адреса"""
    params = {
        "module": "account",
        "action": "tokenbalance",
        "contractaddress": token_address,
        "address": address,
        "tag": "latest",
        "apikey": POLYGONSCAN_API_KEY,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    if data["status"] == "1":
        return int(data["result"])
    else:
        print(f"Ошибка получения баланса для {address}: {data['message']}")
        return 0


def get_last_tx_date(address, token_address):
    """Получаем дату последней транзакции с токеном у адреса"""
    params = {
        "module": "account",
        "action": "tokentx",
        "contractaddress": token_address,
        "address": address,
        "page": 1,
        "offset": 1,
        "sort": "desc",
        "apikey": POLYGONSCAN_API_KEY,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    if data["status"] == "1" and len(data["result"]) > 0:
        timestamp = int(data["result"][0]["timeStamp"])
        from datetime import datetime
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return None


def main():
    # Получим последние 500 Transfer событий (можно увеличить, но API лимит)
    transfers = []
    for page in range(1, 6):
        print(f"Запрос событий, страница {page}...")
        events = get_transfer_events(TOKEN_ADDRESS, page=page, offset=100)
        if not events:
            break
        transfers.extend(events)
        sleep(0.2)  # чтобы не перегрузить API

    # Извлечём адреса получателей (topic2 — адрес получателя)
    holders = set()
    for event in transfers:
        # topic2 содержит адрес получателя в формате hex с префиксом 0x и 64 символами (с ведущими нулями)
        # берем последние 40 символов и приводим к нормальному виду
        to_address = "0x" + event["topics"][2][-40:]
        holders.add(to_address.lower())

    print(f"Найдено уникальных адресов холдеров: {len(holders)}")

    # Получим баланс и дату последней транзакции для каждого адреса
    results = []
    for i, holder in enumerate(holders):
        print(f"[{i+1}/{len(holders)}] Обрабатываем адрес {holder} ...")
        balance = get_balance(holder, TOKEN_ADDRESS)
        if balance == 0:
            continue
        last_tx_date = get_last_tx_date(holder, TOKEN_ADDRESS)
        results.append({"address": holder, "balance": balance, "last_tx": last_tx_date})
        sleep(0.2)

    # Сортируем по балансу
    results.sort(key=lambda x: x["balance"], reverse=True)

    # Выводим топ 10
    for item in results[:10]:
        print(f"Адрес: {item['address']}, Баланс: {item['balance']}, Последняя транзакция: {item['last_tx']}")


if __name__ == "__main__":
    main()
