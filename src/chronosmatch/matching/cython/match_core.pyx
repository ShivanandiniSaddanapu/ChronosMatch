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
