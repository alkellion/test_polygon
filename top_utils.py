import os
import requests
from time import sleep
from datetime import datetime

POLYGONSCAN_API_KEY = os.getenv("POLYGONSCAN_API_KEY")
TOKEN_ADDRESS = os.getenv("TOKEN_ADDRESS")
BASE_URL = "https://api.polygonscan.com/api"


def get_transfer_events(token_address, start_block=0, end_block=99999999, page=1, offset=100):
    params = {
        "module": "logs",
        "action": "getLogs",
        "fromBlock": start_block,
        "toBlock": end_block,
        "address": token_address,
        "topic0": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",  # Transfer event signature
        "page": page,
        "offset": offset,
        "apikey": POLYGONSCAN_API_KEY,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    if data["status"] == "1":
        return data["result"]
    else:
        print(f"Error getting transfer events: {data.get('message')}")
        return []


def get_balance(address, token_address):
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
        print(f"Error getting balance for {address}: {data.get('message')}")
        return 0


def get_last_tx_date(address, token_address):
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
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return None


def get_top_holders_polygonscan(limit=10):
    transfers = []
    for page in range(1, 6):  # максимум 500 событий (5 страниц по 100)
        events = get_transfer_events(TOKEN_ADDRESS, page=page, offset=100)
        if not events:
            break
        transfers.extend(events)
        sleep(0.2)

    holders = set()
    for event in transfers:
        # topic2 — адрес получателя (в формате hex)
        to_address = "0x" + event["topics"][2][-40:]
        holders.add(to_address.lower())

    results = []
    for holder in holders:
        balance = get_balance(holder, TOKEN_ADDRESS)
        if balance == 0:
            continue
        last_tx_date = get_last_tx_date(holder, TOKEN_ADDRESS)
        results.append({"address": holder, "balance": balance, "last_tx": last_tx_date})
        sleep(0.2)

    results.sort(key=lambda x: x["balance"], reverse=True)
    return results[:limit]
