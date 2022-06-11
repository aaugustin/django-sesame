from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

import sesame.utils

def share_booking(request, pk):
    customer = sesame.utils.get_user(request, scope=f"booking:{pk}")
    if customer is None:
        raise PermissionDenied
    booking = get_object_or_404(customer.booking_set, pk=pk)
    return render(request, "bookings/share_booking.html", {"booking": booking})
