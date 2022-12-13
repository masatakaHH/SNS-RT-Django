from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models, transaction
from django.utils import timezone
from datetime import datetime
import pytz
import pyotp
import uuid
import unicodedata
from core.models import *
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

# Genderのラジオボタン用
GenderChoices = (1, "男性"), (2, "女性")

# User_顔画像
def user_displayicon_attachedfilename(instance, filename):
    _user_displayicon_attachedfilename = "users" + "/" + str(
        instance.id) + "/" + "displayicon" + "/"
    _normalized_filename = unicodedata.normalize('NFC', filename)
    return ''.join([_user_displayicon_attachedfilename, _normalized_filename])

class UserDisplayIconImageS3PrivateFileField(models.ImageField):
    """ユーザー_顔画像アップロード用フィールド定義クラス"""

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, height_field=None, width_field=None, **kwargs):
        super().__init__(verbose_name=verbose_name, name=name, upload_to=upload_to, storage=storage, height_field=None, width_field=None, **kwargs)
        # self.storage.default_acl = "private"

class UserManager(BaseUserManager):
    
    
    def create_user(self,username, email=None, password=None, **extra_fields):
        """ Creates and saves User with the given email and password. """
        now = datetime.today().astimezone(pytz.timezone('Asia/Tokyo'))
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(
            username=username,
            email=email,
            is_active=True,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.account_type = 2
        user.set_password(password)
        user.save(using=self._db)        
               
        
        login_url = settings.BACKEND_URL + '/login/' + str(user.id)
        
        # message = Mail(
        #     from_email=settings.EMAIL_FROM,
        #     to_emails=email,
        #     subject='本人確認のためメールアドレスの認証',
        #     html_content='''
        #         本人確認のため、メールアドレス認証が必要です。
        #         確認する。''' + login_url
        # )
        # print(message)
        # try:
        #     sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        #     response = sg.send(message)
        #     print("Send Success")
        # except Exception as e:
        #     print(e)
        return user

    # def create_superuser(self, username, email, password, **extra_fields):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """ Creates and saves a superuser with the given email and password. """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)        

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    """User"""    
    account_type = models.CharField(max_length=26, blank=True, null=True)
    email = models.EmailField(verbose_name=_(u'email address'), max_length=255,blank=True, null=True)
    username = models.CharField(_('username'), max_length=255, blank=True, null=True,unique=True)    
    avatar = models.ImageField(upload_to="user_avatars",blank=True, null=True)    
    email_notification = models.BooleanField(verbose_name=_(u'メール設定'),default=True)    
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    
    created_at = models.DateTimeField(_(u'Created Date At'), editable=False, auto_now_add=True)
    created_by = models.CharField(_(u'Created Person By'), max_length=26, blank=True, null=True)
    updated_at = models.DateTimeField(_(u'Updated Date At'), blank=True, null=True)
    updated_by = models.CharField(_(u'Updated Person By'), max_length=26, blank=True, null=True)
    deleted_at = models.DateTimeField(_(u'Deleted Date At'), blank=True, null=True)
    deleted_by = models.CharField(_(u'Deleted Person By'), max_length=26, blank=True, null=True)
    
    objects = UserManager()    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.username
    
    def get_short_name(self):  
        '''  
        Returns the short name for the user.  
        '''  
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    owner_name = models.CharField(_('キャンペーン主催者名'), max_length=50,blank=True,null=True)
    account_name = models.CharField(verbose_name=_('ユーザー名'),max_length=50,blank=True, null=True)
    brand_name = models.CharField(_('ブランド名'), max_length=50,blank=True,null=True)
    profile_url = models.URLField(verbose_name=_('ブランドURL'),max_length=255,blank=True, null=True)
    header_img = models.ImageField(verbose_name=_('ヘッダー画像'),upload_to="header_imgs")
    contact_form = models.URLField(verbose_name=_('キャンペーンお問い合わせ先'),max_length=255,blank=True, null=True)
    contact_form_email = models.EmailField(blank=True, null=True)
    
# Create your models here.
class TwitterAuthToken(models.Model):
    oauth_token = models.CharField(max_length=255)
    oauth_token_secret = models.CharField(max_length=255)

    def __str__(self):
        return self.oauth_token


class TwitterUser(models.Model):
    twitter_id = models.CharField(max_length=55)
    screen_name = models.CharField(max_length=55)
    name = models.CharField(max_length=55)
    profile_image_url = models.CharField(max_length=255, null=True)
    twitter_oauth_token = models.ForeignKey(TwitterAuthToken, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_notified = models.BooleanField(_("Is notified?"), default=False)

    def __str__(self):
        return self.screen_name
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
