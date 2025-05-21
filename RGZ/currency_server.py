from flask import Flask, jsonify, request

app = Flask(__name__)

CURRENCY_RATES = {
    "USD": 79.85,
    "EUR": 90.44
}


@app.route('/rate', methods=['GET'])
def get_rate():
    currency = request.args.get('currency', '').upper()

    if currency not in CURRENCY_RATES:
        return jsonify({"message": "UNKNOWN CURRENCY"}), 400

    try:
        return jsonify({"rate": CURRENCY_RATES[currency]}), 200
    except Exception:
        return jsonify({"message": "UNEXPECTED ERROR"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)