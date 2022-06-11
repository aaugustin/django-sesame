from django.conf import settings
from django.db import models
from django.urls import reverse

from sesame.utils import get_query_string

class Booking(models.Model):
    name = models.CharField(max_length=100)
    customer = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_private_sharing_link(self):
        link = reverse("share-booking", args=(self.pk,))
        link += get_query_string(user=self.customer, scope=f"booking:{self.pk}")
        return link
