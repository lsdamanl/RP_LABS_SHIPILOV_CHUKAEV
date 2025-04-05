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
    return jsonify({"result": random.random() * param})

#2) Реализовать POST эндпоинт /number/, который принимает в теле
# запроса JSON с полем jsonParam.Вернуть сгенерировать рандомно
# число, умноженное на то, что пришло в JSON и рандомно выбрать
# операцию.

@app.route('/number/', methods=['POST'])
def number_post():
    data = request.get_json()
    json_param = data['jsonParam']
    random_num = random.random()

    operation = random.choice(['+', '-', '*', '/'])

    if operation == '+':
        result = random_num + json_param
    elif operation == '-':
        result = random_num - json_param
    elif operation == '*':
        result = random_num * json_param
    else:
        result = random_num / json_param

    return jsonify({
        "random_number": random_num,
        "operation": operation,
        "input_value": json_param,
        "result": result
    })

# 3) Реализовать DELETE эндпоинт /number/, в ответе сгенерировать
# число и рандомную операцию.

@app.route('/number/', methods=['DELETE'])
def delete_number():
    random_num = random.random()
    operation = random.choice(['+', '-', '*', '/'])

    return jsonify({
        "random_number": random_num,
        "operation": operation
    })


if __name__ == '__main__':
    app.run(debug=True)