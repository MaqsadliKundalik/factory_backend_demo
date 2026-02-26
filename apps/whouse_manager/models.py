from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth.hashers import make_password, check_password
from apps.common.models import BaseModel, UserPermissions
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class WhouseManager(BaseModel):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=25)
    password = models.CharField(max_length=128)
    
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE, related_name='whouse_managers')
    
    # Dynamic Permissions
    permissions = GenericRelation(UserPermissions)

    def has_perm(self, perm_name):
        perm_obj = self.permissions.first()
        if not perm_obj:
            return False
        return getattr(perm_obj, perm_name, False)

    @property
    def is_authenticated(self):
        return True

    def new_session(self):
        from apps.session.models import WhouseManagerSession
        return WhouseManagerSession.for_whouse_manager(self)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name

class WhouseManagerResetPasswordSession(BaseModel):
    whouse_manager = models.ForeignKey(WhouseManager, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=25)
    otp = models.IntegerField(default=123456)
    last_sms_time = models.DateTimeField(auto_now_add=True)
    uses = models.IntegerField(default=0)
    confirmed = models.BooleanField(default=False)
    used = models.BooleanField(default=False)

    @property
    def remaining_attempts(self):
        return 3 - self.uses

    @property
    def expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def send_sms(self):
        # Placeholder for SMS logic
        pass
