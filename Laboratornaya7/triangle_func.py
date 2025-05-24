class IncorrectTriangleSides(Exception):
    pass

def get_triangle_type(a, b, c):
    if any(type(x) not in [int, float] or x <= 0 for x in [a, b, c]):
        raise IncorrectTriangleSides("Sides must be positive numbers.")

    sides = sorted([a, b, c])
    if sides[0] + sides[1] <= sides[2]:
        raise IncorrectTriangleSides("Triangle inequality violated.")

    if a == b == c:
        return "equilateral"
    elif a == b or b == c or a == c:
        return "isosceles"
    else:
        return "nonequilateral"

