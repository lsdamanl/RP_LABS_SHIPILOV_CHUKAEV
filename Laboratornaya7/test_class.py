import pytest
from triangle_class import Triangle, IncorrectTriangleSides

def test_equilateral():
    t = Triangle(3, 3, 3)
    assert t.triangle_type() == "equilateral"
    assert t.perimeter() == 9

def test_isosceles():
    t = Triangle(5, 5, 3)
    assert t.triangle_type() == "isosceles"
    assert t.perimeter() == 13

def test_nonequilateral():
    t = Triangle(4, 5, 6)
    assert t.triangle_type() == "nonequilateral"
    assert t.perimeter() == 15

@pytest.mark.parametrize("a,b,c", [
    (0, 1, 1),
    (-1, 2, 2),
    (1, 2, 3),
    ("a", 2, 2)
])
def test_invalid_triangles(a, b, c):
    with pytest.raises(IncorrectTriangleSides):
        Triangle(a, b, c)
