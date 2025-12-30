from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.contrib.auth.models import BaseUserManager  # <--- Added this import

# --- Added this Manager Class ---
class CustomUserManager(BaseUserManager):
    def create_user(self, user_name, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not user_name:
            raise ValueError('Users must have a username')

        email = self.normalize_email(email)
        user = self.model(
            user_name=user_name,
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_name, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(user_name, email, first_name, last_name, password, **extra_fields)
# -------------------------------

class User(models.Model):
    # --- Connect the Manager Here ---
    objects = CustomUserManager()
    # --------------------------------

    USERNAME_FIELD = 'user_name'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    user_id = models.AutoField(primary_key=True, null=False, editable=False, help_text="User's ID", verbose_name="User ID")
    first_name = models.CharField(max_length=20, null=False, help_text="User's First Name", verbose_name="First Name")
    last_name = models.CharField(max_length=30, null=False, help_text="User's Last Name", verbose_name="Last Name")
    alias = models.CharField(max_length=30, blank=True, null=True, help_text="User's Preferred Reference", verbose_name="Alias")
    email = models.EmailField(max_length=60, unique=True, null=False, help_text="User's Email Address", verbose_name="Email Address")
    user_name = models.CharField(max_length=30, null=False, unique=True, help_text="User's Username", verbose_name="Username")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='last login')
    password = models.CharField(max_length=256, null=False, help_text="User's Password", verbose_name="Password")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True, help_text="Account Created On", verbose_name="Created On")
    updated_on = models.DateField(auto_now=True, help_text="Account Updated On", verbose_name="Updated On")

    def set_password(self, password):
        self.password = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password)

    def __str__(self):
        return self.user_name

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def has_perm(self, perm, obj=None):
        return bool(self.is_superuser)

    def has_perms(self, perm_list, obj=None):
        return bool(self.is_superuser)

    def has_module_perms(self, app_label):
        return bool(self.is_superuser)

    def get_user_permissions(self, obj=None):
        return set()

    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        return {'*'} if self.is_superuser else set()

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text="User's Profile Picture",
        verbose_name="Profile Picture"
    )

    class ThemeChoices(models.TextChoices):
        LIGHT = 'light', 'Light'
        DARK = 'dark', 'Dark'

    theme = models.CharField(
        max_length=10,
        choices=ThemeChoices.choices,
        default=ThemeChoices.LIGHT,
        verbose_name="Site Theme"
    )


    class DisplayNameChoices(models.TextChoices):
        FULL_NAME = 'full', 'Full Name (e.g., John Doe)'
        USERNAME = 'username', 'Username (e.g., johndoe123)'
        ALIAS = 'alias', 'Alias (e.g., Johnny)'

    display_name_preference = models.CharField(
        max_length=10,
        choices=DisplayNameChoices.choices,
        default=DisplayNameChoices.FULL_NAME,
        verbose_name="Display Name Preference"
    )

    @property
    def display_name(self):
        if self.display_name_preference == 'alias' and self.alias:
            return self.alias
        elif self.display_name_preference == 'username':
            return self.user_name
        else:
            return f"{self.first_name} {self.last_name}"