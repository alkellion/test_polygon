

from flask import Flask, request, jsonify

from get_trans_history import get_transaction_history
from token_utils import get_balance, get_balance_batch
from top_utils import get_top_holders_polygonscan

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"message": "Server is running"})


@app.route("/get_balance", methods=["GET"])
def get_balance_route():
    """
    Уровень A: Получение баланса одного адреса
    Пример запроса: GET /get_balance?address=0x...
    """
    address = request.args.get("address")
    if not address:
        return jsonify({"error": "Missing address parameter"}), 400

    balance = get_balance(address)
    return jsonify({"balance": balance})


@app.route("/get_balance_batch", methods=["POST"])
def get_balance_batch_route():
    """
    Уровень B: Получение балансов для нескольких адресов
    Пример запроса: POST /get_balance_batch
    Тело: { "addresses": [ "0x...", "0x..." ] }
    """
    data = request.get_json()
    addresses = data.get("addresses", [])

    if not isinstance(addresses, list) or not addresses:
        return jsonify({"error": "Missing or invalid 'addresses'"}), 400

    balances = get_balance_batch(addresses)
    return jsonify({"balances": balances})


@app.route('/get_top_polygonscan')
def get_top_polygonscan():
    try:
        top_holders = get_top_holders_polygonscan(limit=10)
        return jsonify(top_holders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_transaction_history")
def api_get_transaction_history():
    address = request.args.get("address")
    if not address:
        return jsonify({"error": "Missing address"}), 400

    txs = get_transaction_history(address)
    return jsonify({"transactions": txs})


if __name__ == "__main__":
    # Важно: host=0.0.0.0, чтобы сервер был доступен из Docker
    app.run(host="0.0.0.0", port=8080)
