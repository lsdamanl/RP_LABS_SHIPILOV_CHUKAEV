# Раздел I. Подготовка сервера с API.

#1) Реализовать GET эндпоинт /number/, который принимает параметр
# запроса – param с числом. Вернуть рандомно сгенерированное
# число, умноженное на значение из параметра в формате JSON.

from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/number/')
def number():
    param = float(request.args.get('param'))
    random_num = random.randint(1, 10)
    operation = random.choice(['+', '-', '*', '/'])
    return jsonify({"result": random.random() * param, "operation": operation, 'random_number': random_num})

#2) Реализовать POST эндпоинт /number/, который принимает в теле
# запроса JSON с полем jsonParam.Вернуть сгенерировать рандомно
# число, умноженное на то, что пришло в JSON и рандомно выбрать
# операцию.

@app.route('/number/', methods=['POST'])
def number_post():
    data = request.get_json() or {}
    json_param = data.get('jsonParam')
    if json_param is None:
        return jsonify({"error": "jsonParam is required"}), 400
    try:
        json_param = float(json_param)
    except:
        return jsonify({"error": "jsonParam must be a number"}), 400

    random_num = random.randint(1, 10)
    operation = random.choice(['+', '-', '*', '/'])

    result = json_param * random_num

    return jsonify({
        "input_value": json_param,
        "operation": operation,
        "random_number": random_num,
        "result": result
    })

# 3) Реализовать DELETE эндпоинт /number/, в ответе сгенерировать
# число и рандомную операцию.

@app.route('/number/', methods=['DELETE'])
def delete_number():
    random_num = random.randint(1, 10)
    operation = random.choice(['+', '-', '*', '/'])

    return jsonify({
        "operation": operation,
        "random_number": random_num
    })


if __name__ == '__main__':
    app.run(debug=True)