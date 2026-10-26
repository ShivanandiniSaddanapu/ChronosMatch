
from libc.stdint cimport int64_t
from libc.stdlib cimport malloc, free


cdef struct COrder:
    int64_t order_id
    double price
    int64_t quantity
    int side


# Stores trade results in C memory while matching is in progress.
cdef struct CTrade:
    int64_t buy_order_id
    int64_t sell_order_id
    int64_t quantity
    double price


cdef class CythonOrderBook:
    cdef COrder* orders
    cdef CTrade* trade_buffer
    cdef Py_ssize_t order_count
    cdef Py_ssize_t capacity

    def __cinit__(self, Py_ssize_t capacity=1024):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than zero")

        self.capacity = capacity
        self.order_count = 0

        # Allocate memory for resting orders.
        self.orders = <COrder*>malloc(
            capacity * sizeof(COrder)
        )

        if self.orders == NULL:
            raise MemoryError("Failed to allocate order book")

        # Initialize the trade buffer pointer before allocation.
        self.trade_buffer = NULL

        # Allocate enough trade slots for the maximum possible
        # number of fills from the resting orders in this book.
        self.trade_buffer = <CTrade*>malloc(
            capacity * sizeof(CTrade)
        )

        if self.trade_buffer == NULL:
            free(self.orders)
            self.orders = NULL
            raise MemoryError("Failed to allocate trade buffer")

    def __dealloc__(self):
        if self.orders != NULL:
            free(self.orders)
            self.orders = NULL

        if self.trade_buffer != NULL:
            free(self.trade_buffer)
            self.trade_buffer = NULL

    cpdef add_order(
        self,
        int64_t order_id,
        double price,
        int64_t quantity,
        int side,
    ):
        cdef COrder* order

        if order_id < 0:
            raise ValueError("Order ID must not be negative")

        if price <= 0:
            raise ValueError("Price must be greater than zero")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        if side not in (0, 1):
            raise ValueError("Side must be 0 (BUY) or 1 (SELL)")

        if self.order_count >= self.capacity:
            raise OverflowError("Cython order book is full")

        order = &self.orders[self.order_count]

        order.order_id = order_id
        order.price = price
        order.quantity = quantity
        order.side = side

        self.order_count += 1

    cpdef Py_ssize_t size(self):
        return self.order_count

    cpdef list match_order(
        self,
        int64_t order_id,
        double price,
        int64_t quantity,
        int side,
    ):
        cdef Py_ssize_t i
        cdef Py_ssize_t best_index
        cdef Py_ssize_t trade_count
        cdef COrder* resting
        cdef CTrade* trade
        cdef int64_t trade_quantity
        cdef int64_t remaining
        cdef double best_price
        cdef bint found
        cdef list trades

        if order_id < 0:
            raise ValueError("Order ID must not be negative")

        if price <= 0:
            raise ValueError("Price must be greater than zero")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        if side not in (0, 1):
            raise ValueError("Side must be 0 (BUY) or 1 (SELL)")

        remaining = quantity
        best_index = -1
        trade_count = 0
        found = False
        best_price = 0.0

        # Match orders using C structs. Do not create Python
        # trade tuples inside the matching loop.
        while remaining > 0:
            best_index = -1
            found = False

            for i in range(self.order_count):
                resting = &self.orders[i]

                if resting.quantity <= 0:
                    continue

                if resting.side == side:
                    continue

                if side == 0:
                    # Incoming BUY matches the lowest eligible SELL.
                    if resting.price > price:
                        continue

                    if not found or resting.price < best_price:
                        best_index = i
                        best_price = resting.price
                        found = True

                else:
                    # Incoming SELL matches the highest eligible BUY.
                    if resting.price < price:
                        continue

                    if not found or resting.price > best_price:
                        best_index = i
                        best_price = resting.price
                        found = True

                # Equal-price orders retain time priority:
                # the first eligible order encountered wins.

            if not found:
                break

            resting = &self.orders[best_index]

            if remaining < resting.quantity:
                trade_quantity = remaining
            else:
                trade_quantity = resting.quantity

            # Store the trade in the preallocated C buffer.
            # Convert to Python tuples only after matching finishes.
            if trade_count >= self.capacity:
                raise OverflowError("Cython trade buffer is full")

            trade = &self.trade_buffer[trade_count]

            if side == 0:
                # Incoming order is BUY; resting order is SELL.
                trade.buy_order_id = order_id
                trade.sell_order_id = resting.order_id
            else:
                # Resting order is BUY; incoming order is SELL.
                trade.buy_order_id = resting.order_id
                trade.sell_order_id = order_id

            trade.quantity = trade_quantity
            trade.price = resting.price

            trade_count += 1

            remaining -= trade_quantity
            resting.quantity -= trade_quantity

            if resting.quantity == 0:
                self._remove_order(best_index)

        # Preserve any unmatched incoming quantity in the book.
        if remaining > 0:
            self._add_remaining_order(
                order_id,
                price,
                remaining,
                side,
            )

        # Convert C trade records into the same list-of-tuples
        # format expected by the existing adapter and tests.
        trades = []

        for i in range(trade_count):
            trade = &self.trade_buffer[i]

            trades.append(
                (
                    trade.buy_order_id,
                    trade.sell_order_id,
                    trade.quantity,
                    trade.price,
                )
            )

        return trades

    cdef void _remove_order(self, Py_ssize_t index):
        cdef Py_ssize_t i

        for i in range(index, self.order_count - 1):
            self.orders[i] = self.orders[i + 1]

        self.order_count -= 1

    cdef void _add_remaining_order(
        self,
        int64_t order_id,
        double price,
        int64_t quantity,
        int side,
    ):
        cdef COrder* order

        if self.order_count >= self.capacity:
            raise OverflowError("Cython order book is full")

        order = &self.orders[self.order_count]

        order.order_id = order_id
        order.price = price
        order.quantity = quantity
        order.side = side

        self.order_count += 1


cpdef int match_quantity(
    int incoming_quantity,
    int resting_quantity,
):
    cdef int trade_quantity

    if incoming_quantity < resting_quantity:
        trade_quantity = incoming_quantity
    else:
        trade_quantity = resting_quantity

    return trade_quantity
