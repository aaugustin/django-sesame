from django.utils.decorators import method_decorator
from django.views.generic import DetailView

from sesame.decorators import authenticate

@method_decorator(authenticate(scope="booking:{pk}"), name="dispatch")
class ShareBooking(DetailView):

    template_name = "bookings/share_booking.html"

    def get_queryset(self):
        return self.request.user.booking_set
