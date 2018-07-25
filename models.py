from django.db import models
from django.contrib.auth.models import User
import datetime
import uuid


#Block User List
class BlockedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user')
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at =models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.blocked_user
    def __unicode__(self):
            return u"%d %s" % (self.pk, self.privacy_description)
    class Meta:
         db_table = "block_users"
         verbose_name_plural = "Blocked Users"


#Privacy settings
class PrivacyType(models.Model):
    privacy_description = models.CharField(max_length=50,blank=False,unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at =models.DateTimeField(auto_now=True, editable=False)
    def __str__(self):
        return self.privacy_description
    def __unicode__(self):
            return u"%d %s" % (self.pk, self.privacy_description)
    class Meta:
         db_table = "privacy_types"
         verbose_name_plural = "Privacy Types"

# User Provacy Setting
class UserPrivacy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='privacyuser')
    privacytype = models.ForeignKey(PrivacyType,on_delete=models.CASCADE,null=True, verbose_name="Privacy Types",related_name='+privacytype+')
    privacyon = models.ForeignKey(PrivacyOn,on_delete=models.CASCADE, null=True, verbose_name="Privacy Event Types",related_name='+privacyevent+')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at =models.DateTimeField(auto_now=True, editable=False)
    def __str__(self):
         return '{}'.format(self.privacyon)
    def __unicode__(self):
         return u"%d %s %s" % (self.pk, self.privacytype, self.privacyon)
    def privacyType(self):
         return UserPrivacy.objects.filter(privacytype=self)
    class Meta:
         db_table = "user_privacy"
         verbose_name_plural = "User Privacy"
