
import curses
import time

from chronosmatch.matching.engine import MatchingEngine, Trade
from chronosmatch.matching.order import Order, OrderSide
from chronosmatch.monitoring.performance_metrics import PerformanceMetrics


SYMBOL = "AAPL"
REFRESH_SECONDS = 0.1
WHALE_ORDER_ID = 6


def detect_whale_sweep(
    order: Order,
    trades: list[Trade],
    submitted_quantity: int,
) -> dict | None:
    """Describe an order that executes across multiple price levels."""
    if not trades:
        return None

    price_levels = {trade.price for trade in trades}

    if len(price_levels) < 2:
        return None

    return {
        "order_id": order.order_id,
        "side": order.side.value,
        "levels": len(price_levels),
        "quantity": sum(trade.quantity for trade in trades),
        "submitted_quantity": submitted_quantity,
        "prices": sorted(price_levels, reverse=order.side == OrderSide.SELL),
    }


def build_demo_engine(
    metrics: PerformanceMetrics | None = None,
) -> MatchingEngine:
    engine = MatchingEngine()
    engine.last_whale_event = None

    # Establish a two-sided book.
    demo_orders = [
        Order.create(1, SYMBOL, OrderSide.BUY, 149.00, 100),
        Order.create(2, SYMBOL, OrderSide.BUY, 148.50, 75),
        Order.create(3, SYMBOL, OrderSide.SELL, 150.00, 40),
        Order.create(4, SYMBOL, OrderSide.SELL, 151.00, 60),
        Order.create(5, SYMBOL, OrderSide.SELL, 152.00, 50),
    ]

    # A large buy order sweeps the three resting ask price levels.
    whale_order = Order.create(
        WHALE_ORDER_ID,
        SYMBOL,
        OrderSide.BUY,
        153.00,
        180,
    )
    demo_orders.append(whale_order)

    for order in demo_orders:
        submitted_quantity = order.quantity

        start_ns = time.perf_counter_ns()
        trades = engine.submit(order)
        latency_ns = time.perf_counter_ns() - start_ns

        if metrics is not None:
            metrics.record_submission(latency_ns, len(trades))

        event = detect_whale_sweep(
            order,
            trades,
            submitted_quantity,
        )

        if event is not None:
            engine.last_whale_event = event

    return engine


def draw_dashboard(
    screen,
    engine: MatchingEngine,
    start_time: float,
    metrics: PerformanceMetrics,
    whale_attr: int = curses.A_BOLD,
) -> None:
    screen.erase()

    screen.addstr(0, 2, "========================================")
    screen.addstr(1, 2, "       CHRONOSMATCH LATENCY DASHBOARD")
    screen.addstr(2, 2, "========================================")
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
        mid_price = (best_ask + best_bid) / 2
        screen.addstr(13, 2, f"Spread:    {spread:.2f}")
        screen.addstr(14, 2, f"Mid Price: {mid_price:.2f}")
    else:
        screen.addstr(13, 2, "Spread:    ---")
        screen.addstr(14, 2, "Mid Price: ---")

    screen.addstr(16, 2, "DEMO MATCHING METRICS")
    screen.addstr(17, 2, f"Orders submitted: {metrics.orders_submitted}")
    screen.addstr(18, 2, f"Trades executed:  {metrics.trades_executed}")
    screen.addstr(
        19, 2,
        f"Average latency:  {metrics.average_latency_ns:.0f} ns",
    )
    screen.addstr(
        20, 2,
        f"Maximum latency:  {metrics.max_latency_ns} ns",
    )

    event = engine.last_whale_event

    if event is not None:
        screen.addstr(
            22, 2,
            "!!! WHALE ORDER: MULTI-LEVEL SWEEP !!!",
            whale_attr,
        )
        screen.addstr(
            23, 2,
            f"Order #{event['order_id']} ({event['side']}): "
            f"{event['quantity']} shares across "
            f"{event['levels']} price levels",
            whale_attr,
        )
        screen.addstr(
            24, 2,
            "Execution prices: "
            + ", ".join(f"{price:.2f}" for price in event["prices"]),
        )
    else:
        screen.addstr(22, 2, "No multi-level whale sweep detected.")

    elapsed = time.perf_counter() - start_time
    screen.addstr(26, 2, f"Dashboard uptime: {elapsed:.1f}s")
    screen.addstr(28, 2, "Press Q to quit")

    screen.refresh()


def dashboard(screen) -> None:
    curses.curs_set(0)
    screen.nodelay(True)

    metrics = PerformanceMetrics()
    engine = build_demo_engine(metrics)
    start_time = time.perf_counter()

    whale_attr = curses.A_BOLD

    if curses.has_colors():
        try:
            curses.start_color()
            curses.init_pair(
                1,
                curses.COLOR_RED,
                curses.COLOR_BLACK,
            )
            whale_attr = curses.color_pair(1) | curses.A_BOLD
        except curses.error:
            pass

    while True:
        draw_dashboard(
            screen,
            engine,
            start_time,
            metrics,
            whale_attr,
        )

        key = screen.getch()
        if key in (ord("q"), ord("Q")):
            break

        time.sleep(REFRESH_SECONDS)


def main() -> None:
    curses.wrapper(dashboard)


if __name__ == "__main__":
    main()
