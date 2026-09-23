import curses
import time

from chronosmatch.matching.engine import MatchingEngine
from chronosmatch.matching.order import Order, OrderSide


SYMBOL = "AAPL"
REFRESH_SECONDS = 0.1


def build_demo_engine() -> MatchingEngine:
    engine = MatchingEngine()

    engine.submit(
        Order.create(
            1,
            SYMBOL,
            OrderSide.BUY,
            149.00,
            100,
        )
    )

    engine.submit(
        Order.create(
            2,
            SYMBOL,
            OrderSide.BUY,
            148.50,
            75,
        )
    )

    engine.submit(
        Order.create(
            3,
            SYMBOL,
            OrderSide.SELL,
            151.00,
            80,
        )
    )

    engine.submit(
        Order.create(
            4,
            SYMBOL,
            OrderSide.SELL,
            152.00,
            60,
        )
    )

    return engine


def draw_dashboard(
    screen,
    engine: MatchingEngine,
    start_time: float,
) -> None:
    screen.clear()

    screen.addstr(
        0,
        2,
        "========================================",
    )
    screen.addstr(
        1,
        2,
        "       CHRONOSMATCH LATENCY DASHBOARD",
    )
    screen.addstr(
        2,
        2,
        "========================================",
    )

    screen.addstr(4, 2, f"Symbol: {SYMBOL}")

    best_bid = engine.order_book.best_bid()
    best_ask = engine.order_book.best_ask()

    screen.addstr(6, 2, "             ORDER BOOK")
    screen.addstr(7, 2, "----------------------------------------")
    screen.addstr(8, 10, "BID")
    screen.addstr(8, 28, "ASK")

    screen.addstr(
        9,
        8,
        f"{best_bid:>10.2f}" if best_bid is not None else "       ---",
    )
    screen.addstr(
        9,
        26,
        f"{best_ask:>10.2f}" if best_ask is not None else "       ---",
    )

    bid_quantity = (
        sum(order.quantity for order in engine.order_book.bids[best_bid])
        if best_bid is not None
        else 0
    )

    ask_quantity = (
        sum(order.quantity for order in engine.order_book.asks[best_ask])
        if best_ask is not None
        else 0
    )

    screen.addstr(10, 8, f"{bid_quantity:>10}")
    screen.addstr(10, 26, f"{ask_quantity:>10}")

    screen.addstr(11, 2, "----------------------------------------")

    if best_bid is not None and best_ask is not None:
        spread = best_ask - best_bid
        mid_price = (best_bid + best_ask) / 2

        screen.addstr(13, 2, f"Spread:    {spread:.2f}")
        screen.addstr(14, 2, f"Mid Price: {mid_price:.2f}")
    else:
        screen.addstr(13, 2, "Spread:    ---")
        screen.addstr(14, 2, "Mid Price: ---")

    elapsed = time.perf_counter() - start_time

    screen.addstr(16, 2, f"Dashboard uptime: {elapsed:.1f}s")
    screen.addstr(18, 2, "Press Q to quit")

    screen.refresh()


def dashboard(screen) -> None:
    curses.curs_set(0)
    screen.nodelay(True)

    engine = build_demo_engine()
    start_time = time.perf_counter()

    while True:
        draw_dashboard(
            screen,
            engine,
            start_time,
        )

        key = screen.getch()

        if key in (ord("q"), ord("Q")):
            break

        time.sleep(REFRESH_SECONDS)


def main() -> None:
    curses.wrapper(dashboard)


if __name__ == "__main__":
    main()
