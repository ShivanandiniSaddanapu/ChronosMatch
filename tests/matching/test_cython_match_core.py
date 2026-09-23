from chronosmatch.matching.cython.match_core import CythonOrderBook


def test_add_order_and_size():
    book = CythonOrderBook()

    book.add_order(1, 100.0, 50, 0)
    book.add_order(2, 101.0, 75, 1)

    assert book.size() == 2


def test_buy_matches_lowest_sell_price_first():
    book = CythonOrderBook()

    book.add_order(1, 101.0, 50, 1)
    book.add_order(2, 100.0, 50, 1)

    trades = book.match_order(3, 101.0, 50, 0)

    assert trades == [
        (3, 2, 50, 100.0),
    ]


def test_sell_matches_highest_buy_price_first():
    book = CythonOrderBook()

    book.add_order(1, 99.0, 50, 0)
    book.add_order(2, 100.0, 50, 0)

    trades = book.match_order(3, 99.0, 50, 1)

    assert trades == [
        (3, 2, 50, 100.0),
    ]


def test_time_priority_at_same_price():
    book = CythonOrderBook()

    book.add_order(1, 100.0, 30, 1)
    book.add_order(2, 100.0, 40, 1)

    trades = book.match_order(3, 100.0, 50, 0)

    assert trades == [
        (3, 1, 30, 100.0),
        (3, 2, 20, 100.0),
    ]


def test_partial_fill():
    book = CythonOrderBook()

    book.add_order(1, 100.0, 100, 1)

    trades = book.match_order(2, 100.0, 40, 0)

    assert trades == [
        (2, 1, 40, 100.0),
    ]

    assert book.size() == 1


def test_multiple_price_levels():
    book = CythonOrderBook()

    book.add_order(1, 100.0, 50, 1)
    book.add_order(2, 101.0, 75, 1)

    trades = book.match_order(3, 101.0, 60, 0)

    assert trades == [
        (3, 1, 50, 100.0),
        (3, 2, 10, 101.0),
    ]

    assert book.size() == 1


def test_unmatched_order_is_added_to_book():
    book = CythonOrderBook()

    trades = book.match_order(1, 100.0, 50, 0)

    assert trades == []
    assert book.size() == 1


def test_non_crossing_order_remains_resting():
    book = CythonOrderBook()

    book.add_order(1, 105.0, 50, 1)

    trades = book.match_order(2, 100.0, 50, 0)

    assert trades == []
    assert book.size() == 2


def test_full_fill_removes_resting_order():
    book = CythonOrderBook()

    book.add_order(1, 100.0, 50, 1)

    trades = book.match_order(2, 100.0, 50, 0)

    assert trades == [
        (2, 1, 50, 100.0),
    ]

    assert book.size() == 0