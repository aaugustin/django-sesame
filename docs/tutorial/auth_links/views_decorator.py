from django.shortcuts import get_object_or_404, render

from sesame.decorators import authenticate

@authenticate(scope="booking:{pk}")
def share_booking(request, pk):
    booking = get_object_or_404(request.user.booking_set, pk=pk)
    return render(request, "bookings/share_booking.html", {"booking": booking})
