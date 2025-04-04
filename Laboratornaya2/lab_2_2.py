# Задание 2.2
# 1. Считать с клавиатуры произвольную строку.
# 2. Заменить в строке все символы двоеточия символом процента.
# 3. Вывести в консоль количество замен

input_string = input("Введите строку: ")
modified_string = input_string.replace(":", "%")
replace_count = len(input_string) - len(modified_string.replace("%", ":"))

print("Модифицированная строка:", modified_string)
print("Количество замен:", replace_count)
