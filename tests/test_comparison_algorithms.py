from app.compare import ORBStrategy, HistogramStrategy, PHashStrategy

def test_orb_strategy():
    """Тест стратегии ORB"""
    strategy = ORBStrategy()
    similarity = strategy.compare("tests/images/test1.jpg", "tests/images/test2.jpg")
    assert 0 <= similarity <= 1

def test_histogram_strategy():
    """Тест стратегии гистограмм"""
    strategy = HistogramStrategy()
    similarity = strategy.compare("tests/images/test1.jpg", "tests/images/test2.jpg")
    assert 0 <= similarity <= 1

def test_phash_strategy():
    """Тест стратегии pHash"""
    strategy = PHashStrategy()
    similarity = strategy.compare("tests/images/test1.jpg", "tests/images/test2.jpg")
    assert 0 <= similarity <= 1
