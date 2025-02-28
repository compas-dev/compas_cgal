import compas_cgal

def test_add():
    print(compas_cgal.add(1, 2))
    assert compas_cgal.add(1, 2) == 3


print(compas_cgal.__doc__)