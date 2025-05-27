import os
import requests
from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv

# Загружаем .env переменные
load_dotenv()

# Обязательные переменные из окружения
polygonscan_api_key = os.getenv('POLYGONSCAN_API_KEY')
raw_token_address = os.getenv('TOKEN_ADDRESS')

# Приводим адрес токена к checksum-формату
token_address = Web3.to_checksum_address(raw_token_address)


def get_transaction_history(address: str) -> list[dict]:
    url = (
        f"https://api.polygonscan.com/api"
        f"?module=account"
        f"&action=tokentx"
        f"&contractaddress={token_address}"
        f"&address={address}"
        f"&page=1"
        f"&offset=100"
        f"&sort=desc"
        f"&apikey={polygonscan_api_key}"
    )

    response = requests.get(url)
    data = response.json()

    if data.get("status") != "1":
        return []

    result = []
    for tx in data["result"]:
        result.append({
            "hash": tx["hash"],
            "from": tx["from"],
            "to": tx["to"],
            "value": int(tx["value"]) / (10 ** int(tx["tokenDecimal"])),
            "timestamp": datetime.fromtimestamp(int(tx["timeStamp"])).strftime("%Y-%m-%d %H:%M:%S")
        })

    return result
