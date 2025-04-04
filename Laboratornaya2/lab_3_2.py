#1. Считать из параметров командной строки одномерный массив,
#состоящий из N целочисленных элементов.
#2. Найти минимальный элемент.
#3. Вывести индекс минимального элемента на экран.
#4. Вывести в одну строку все положительные числа массива.
#5. Вывести в одну строку все отрицательные числа массива

import sys

if len(sys.argv) < 2:
    sys.exit("Ошибка: укажите числа через пробел")

numbers = []
for arg in sys.argv[1:]:
    is_valid = True
    start_idx = 0

    if arg[0] == '-':
        if len(arg) == 1:
            is_valid = False
        start_idx = 1

    for i in range(start_idx, len(arg)):
        if not arg[i].isdigit():
            is_valid = False
            break

    if is_valid:
        numbers.append(int(arg))
    else:
        sys.exit(f"Ошибка: '{arg}' не является целым числом")

if not numbers:
    sys.exit("Массив пуст")

min_index = 0
min_value = numbers[0]

for i in range(1, len(numbers)):
    if numbers[i] < min_value:
        min_value = numbers[i]
        min_index = i

print(f"Индекс минимального элемента: {min_index}")

positives = []
for num in numbers:
    if num > 0:
        positives.append(str(num))
print("Положительные числа:", " ".join(positives) if positives else "нет")

negatives = []
for num in numbers:
    if num < 0:
        negatives.append(str(num))
print("Отрицательные числа:", " ".join(negatives) if negatives else "нет")