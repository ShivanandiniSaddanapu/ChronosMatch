from libc.stdint cimport int64_t
from libc.stdlib cimport malloc, free


cdef struct COrder:
    int64_t order_id
    double price
    int64_t quantity
    int side


cdef class CythonOrderBook:
    cdef COrder* orders
    cdef Py_ssize_t order_count
    cdef Py_ssize_t capacity

    def __cinit__(self, Py_ssize_t capacity=1024):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than zero")

        self.capacity = capacity
        self.order_count = 0

        self.orders = <COrder*>malloc(
            capacity * sizeof(COrder)
        )

        if self.orders == NULL:
            raise MemoryError("Failed to allocate order book")

    def __dealloc__(self):
        if self.orders != NULL:
            free(self.orders)
            self.orders = NULL

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
        cdef COrder* resting
        cdef int64_t trade_quantity
        cdef int64_t remaining
        cdef double best_price
        cdef bint found

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
        found = False
        best_price = 0.0

        trades = []

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
                    # Incoming BUY matches lowest SELL price.
                    if resting.price > price:
                        continue

                    if not found or resting.price < best_price:
                        best_index = i
                        best_price = resting.price
                        found = True

                else:
                    # Incoming SELL matches highest BUY price.
                    if resting.price < price:
                        continue

                    if not found or resting.price > best_price:
                        best_index = i
                        best_price = resting.price
                        found = True

                # Same price:
                # The earlier order remains preferred because
                # we scan the order book from oldest to newest.

            if not found:
                break

            resting = &self.orders[best_index]

            if remaining < resting.quantity:
                trade_quantity = remaining
            else:
                trade_quantity = resting.quantity

            if side == 0:
                trades.append(
                    (
                        order_id,
                        resting.order_id,
                        trade_quantity,
                        resting.price,
                    )
                )
            else:
                trades.append(
                    (
                        resting.order_id,
                        order_id,
                        trade_quantity,
                        resting.price,
                    )
                )

            remaining -= trade_quantity
            resting.quantity -= trade_quantity

            if resting.quantity == 0:
                self._remove_order(best_index)

        if remaining > 0:
            self._add_remaining_order(
                order_id,
                price,
                remaining,
                side,
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
