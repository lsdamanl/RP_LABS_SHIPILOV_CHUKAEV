class IncorrectTriangleSides(Exception):
    pass


class Triangle:
    def __init__(self, a, b, c):
        # Проверка корректности типов и положительности
        if any(type(x) not in [int, float] or x <= 0 for x in [a, b, c]):
            raise IncorrectTriangleSides("Sides must be positive numbers.")

        # Сортировка после проверки, чтобы использовать в неравенстве треугольника
        self.sides = sorted([a, b, c])
        if self.sides[0] + self.sides[1] <= self.sides[2]:
            raise IncorrectTriangleSides("Triangle inequality violated.")

        self.a, self.b, self.c = a, b, c

    def triangle_type(self):
        if self.a == self.b == self.c:
            return "equilateral"
        elif self.a == self.b or self.b == self.c or self.a == self.c:
            return "isosceles"
        else:
            return "nonequilateral"

    def perimeter(self):
        return self.a + self.b + self.c
