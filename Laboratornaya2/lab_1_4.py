#Считать с клавиатуры непустую произвольную последовательность
#целых чисел. Найти:
#i. Сумму всех чисел последовательности (решить задачу
#используя циклическую конструкцию while)
#ii. Количество всех чисел последовательности (решить задачу
#используя циклическую конструкцию while)


sum_of_numbers = 0
count_of_numbers = 0

print("Введите последовательность целых чисел (вводите числа по одному). Для завершения введите 'q':")

while True:
    user_input = input()
    if user_input == 'q' or user_input == '':
        break

    is_valid = True
    start_index = 0

    if user_input and user_input[0] == '-':
        if len(user_input) == 1:
            is_valid = False
        start_index = 1

    for i in range(start_index, len(user_input)):
        if not user_input[i].isdigit():
            is_valid = False
            break

    if is_valid:
        num = int(user_input)
        sum_of_numbers += num
        count_of_numbers += 1
    else:
        print("Ошибка: введено не число!")

print(f"Сумма: {sum_of_numbers}")
print(f"Количество: {count_of_numbers}")