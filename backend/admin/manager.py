from django.contrib.auth.models import BaseUserManager

class AdminManager(BaseUserManager):
    def create_admin(self, email, password=None, **extra_fields):
        """
        Creates and saves an admin user with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        admin = self.model(email=email, **extra_fields)
        admin.set_password(password)
        admin.save(using=self._db)
        return admin
