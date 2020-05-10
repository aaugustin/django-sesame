import uuid

from django.contrib.auth import models as auth_models
from django.db import models


class BigAutoUser(auth_models.AbstractBaseUser):
    id = models.BigAutoField(primary_key=True)
    is_active = models.BooleanField(default=True)
    username = models.CharField(max_length=32, unique=True)

    USERNAME_FIELD = "username"


class UUIDUser(auth_models.AbstractBaseUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    is_active = models.BooleanField(default=True)
    username = models.CharField(max_length=32, unique=True)

    USERNAME_FIELD = "username"


class BooleanUser(auth_models.AbstractBaseUser):
    username = models.BooleanField(primary_key=True)  # pathological!

    USERNAME_FIELD = "username"


class StrUser(auth_models.AbstractBaseUser):
    username = models.CharField(primary_key=True, max_length=24)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "username"
