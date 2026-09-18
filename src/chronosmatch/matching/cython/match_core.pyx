cpdef int match_quantity(int incoming_quantity, int resting_quantity):
    cdef int trade_quantity

    if incoming_quantity < resting_quantity:
        trade_quantity = incoming_quantity
    else:
        trade_quantity = resting_quantity

    return trade_quantity
