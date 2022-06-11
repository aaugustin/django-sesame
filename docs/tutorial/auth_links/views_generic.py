from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView

import sesame.utils

class ShareBooking(DetailView):

    template_name = "bookings/share_booking.html"

    def get(self, request, pk):
        self.customer = sesame.utils.get_user(request, scope=f"booking:{pk}")
        if self.customer is None:
            raise PermissionDenied
        return super().get(request, pk=pk)

    def get_queryset(self):
        return self.customer.booking_set
