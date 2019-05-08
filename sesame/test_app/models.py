from __future__ import unicode_literals

import uuid

from django.contrib.auth import models as auth_models
from django.db import models


class UUIDUser(auth_models.AbstractBaseUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    is_active = models.BooleanField(default=True)
    username = models.CharField(max_length=32, unique=True)

    USERNAME_FIELD = "username"


class CharUser(auth_models.AbstractBaseUser):
    username = models.CharField(max_length=32, primary_key=True)

    USERNAME_FIELD = "username"
