from web3 import Web3
import json
from config import polygon_rpc, token_address_main, abi_path

# Загружаем ABI
with open(abi_path) as f:
    ERC20_ABI = json.load(f)

# Подключаемся к Polygon
web3 = Web3(Web3.HTTPProvider(polygon_rpc))

# Создаём объект контракта токена по адресу
token_contract = web3.eth.contract(
    address=Web3.to_checksum_address(token_address_main),
    abi=ERC20_ABI
)

# Получаем количество десятичных знаков токена (обычно 18)
decimals = token_contract.functions.decimals().call()


def get_balance(address: str) -> float:

    """
    Получаем баланс токена TBY для одного адреса

    :param address: Адрес кошелька
    :return: Баланс в float с учётом десятичных знаков токена
    """

    address = Web3.to_checksum_address(address)
    raw_balance = token_contract.functions.balanceOf(address).call()

    return raw_balance / (10 ** decimals)


def get_balance_batch(addresses: list[str]) -> list[float]:

    """
    Получаем балансы токена TBY для списка адресов

    :param addresses: Список адресов
    :return: Список балансов в float
    """

    return [get_balance(addr) for addr in addresses]


def get_token_info(token_address: str) -> dict:

    """
    Получаем информацию о токене ERC20

    :param token_address: Адрес токена
    :return: Словарь с symbol, name, totalSupply
    """

    token = web3.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=ERC20_ABI
    )

    return {
        "symbol": token.functions.symbol().call(),
        "name": token.functions.name().call(),
        "totalSupply": token.functions.totalSupply().call() / (10 ** decimals)
    }
