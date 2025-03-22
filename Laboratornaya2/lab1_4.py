#Считать с клавиатуры непустую произвольную последовательность
#целых чисел. Найти:
#i. Сумму всех чисел последовательности (решить задачу
#используя циклическую конструкцию while)
#ii. Количество всех чисел последовательности (решить задачу
#используя циклическую конструкцию while)

numbers = []
sum_of_numbers = 0
count_of_numbers = 0

print("Введите последовательность целых чисел (для завершения введите пустую строку):")
while True:
    user_input = input()
    if user_input == "" or not user_input.isnumeric():
        break
    number = int(user_input)
    numbers.append(number)


index = 0
while index < len(numbers):
    sum_of_numbers += numbers[index]
    count_of_numbers += 1
    index += 1

print(f"Сумма всех чисел последовательности: {sum_of_numbers}")
print(f"Количество всех чисел последовательности: {count_of_numbers}")