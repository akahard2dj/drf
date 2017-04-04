from django.db import models
from django.core import validators
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from django.utils import timezone

from core.utils import random_digit_and_number
from core.models.category import (University, Department)


class DonkeyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.is_confirm = True
        user.save(using=self._db)

        return user


class DonkeyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    nickname = models.CharField(null=False, max_length=100, default=random_digit_and_number)
    university = models.ForeignKey(University)
    #department = models.OneToOneField(Department)
    #name_tag = models.ManyToManyField(NameTag, through='NameTag')
    created_at = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_confirm = models.BooleanField(default=False)

    objects = DonkeyUserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):  # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        key_email = kwargs.pop('key_email')
        email_domain = key_email.split('@')[-1]
        try:
            univ_from_db = University.objects.get(domain=email_domain)
        except University.DoesNotExist:
            raise validators.ValidationError('Not in university')
        else:
            self.email = key_email
            self.university = univ_from_db
            super(DonkeyUser, self).save(*args, **kwargs)
        '''
        user.nickname = random_digit_and_number()
            user_domain = key_email.split('@')[-1]
            univ_from_db = University.objects.get(domain=user_domain)

            user.university = univ_from_db

            #user.department = Department.objects.get(pk=1)
            user.email = key_email
        '''
