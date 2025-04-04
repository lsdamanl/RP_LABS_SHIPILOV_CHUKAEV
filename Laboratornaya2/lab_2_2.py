# Задание 2.2
# 1. Считать с клавиатуры произвольную строку.
# 2. Заменить в строке все символы двоеточия символом процента.
# 3. Вывести в консоль количество замен

input_string = input("Введите строку: ")
replace_count = input_string.count(":")
modified_string = input_string.replace(":", "%")

print("Модифицированная строка:", modified_string)
print("Количество замен:", replace_count)
