from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, \
    PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        """Creates and save a User with email and password"""
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """Creates and saves a new superuser"""
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='Email address', max_length=255, blank=False, unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(name='password', max_length=1000)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        return self.email
