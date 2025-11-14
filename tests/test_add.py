from app_demo import add

def test_add_positive():
    assert add(2, 3) == 5

def test_add_zero():
    assert add(0, 0) == 0

def test_multiply():
    from app_demo import multiply
    assert multiply(3, 4) == 12
