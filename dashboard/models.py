from django.conf import settings
from django.dispatch import receiver
from django.db import models, transaction
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import datetime
import pytz
import uuid
import ulid
import os
from accounts.models import User

class ULIDField(models.CharField):
    """ULIDフィールドの定義"""

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 8
        super(ULIDField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'char(8)'

# 抽選方式
CastTypeChoices = (1, "インスタントウィン"), (2, "後日抽選")
class Campaign(models.Model):
    id = ULIDField(
        primary_key = True,
        default = ulid.new,
        editable = False)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    casttype = models.IntegerField(verbose_name=_(u'抽選方式'),choices=CastTypeChoices)
    title = models.CharField(max_length=100)
    context = models.TextField()
    sdate = models.DateTimeField(_(u'公開日時'), blank=True, null=True)
    edate = models.DateTimeField(_(u'終了日時'), blank=True, null=True)
    instancewin = models.IntegerField(default=0)
    missing_img = models.ImageField(upload_to="missing_images", blank=True, null=True)
    is_publish = models.BooleanField(default=False)
    is_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(_(u'Created Date At'), editable=False, auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(_(u'Updated Date At'), blank=True, null=True)
    
    def __str__(self):
        return self.title
    
class CreativeFile(models.Model):
    campaign = models.ForeignKey(Campaign,on_delete=models.CASCADE)
    file = models.ImageField(upload_to="creative_files")
    
    def __str__(self,obj):
        return self.campaign.title
    
class TwitterAction(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=256, blank=True, null=True)
    action_id = models.IntegerField(unique=True)
    
    def __str__(self):
        return self.name

class CampaignAction(models.Model):
    campaign = models.ForeignKey(Campaign,on_delete=models.CASCADE)
    action_name = models.ForeignKey(TwitterAction,on_delete=models.CASCADE)
    screen_name = models.CharField(max_length=20, blank=True, null=True)
    retweet_url = models.URLField(blank=True, null=True)
    tweet_title = models.TextField(max_length=256, blank=True, null=True)
    tweet_img = models.ImageField(upload_to="tweet_images", blank=True, null=True)
    campaign_url = models.BooleanField(default=False)
    
    def __str__(self,obj):
        return obj.campaign.title
    
# class TempCampaignAction(models.Model):
#     user = models.ForeignKey(User,on_delete=models.CASCADE)
#     action_name = models.ForeignKey(TwitterAction,on_delete=models.CASCADE)
#     twitter_id = models.CharField(max_length=20, blank=True, null=True)
#     retweet_url = models.URLField(blank=True, null=True)
#     tweet_title = models.TextField(max_length=256, blank=True, null=True)
#     tweet_img = models.ImageField(upload_to="tweet_images", blank=True, null=True)
#     campaign_url = models.BooleanField(default=False)
    
#     def __str__(self,obj):
#         return obj.campaign.title
    
# ギフトの種類
GiftChoices = (1, "デジタル"), (2, "クーポン"), (3, "賞品"), (4, "ダウンロード")
class DigitalGift(models.Model):
    campaign = models.ForeignKey(Campaign,on_delete=models.CASCADE)
    title = models.CharField(max_length=40, blank=True, null=True)
    image = models.ImageField(upload_to="gift_files", blank=True, null=True)
    codetype = models.CharField(_(u'コードタイプ'),max_length=40, blank=True, null=True)
    candidate_num = models.IntegerField(_(u'当選者数'),default=1)
    color = models.CharField(_(u'ギフトカラー'),max_length=6, blank=True, null=True)
    receipt_date = models.DateField(_(u'受取期限'), blank=True, null=True)
    sdate = models.DateTimeField(_(u'有効期間/開始'), blank=True, null=True)
    edate = models.DateTimeField(_(u'有効期間/終了'), blank=True, null=True)
    detail = models.URLField(_(u'詳細URL'),blank=True, null=True)
    money = models.IntegerField(_(u'ギフト金額'),default=0)
    useterm_doc = models.TextField()
    attention_doc = models.TextField()
    created_at = models.DateTimeField(_(u'Created Date At'), editable=False, auto_now_add=True, blank=True, null=True)
    
    def __str__(self):
        return self.title
    
# class TempDigitalGift(models.Model):
#     user = models.ForeignKey(User,on_delete=models.CASCADE)
#     title = models.CharField(max_length=40)
#     image = models.ImageField(upload_to="gift_files")
#     codetype = models.CharField(_(u'コードタイプ'),max_length=40)
#     candidate_num = models.IntegerField(_(u'当選者数'),default=1)
#     color = models.CharField(_(u'ギフトカラー'),max_length=6)
#     receipt_date = models.DateField(_(u'受取期限'), blank=True, null=True)
#     sdate = models.DateTimeField(_(u'有効期間/開始'), blank=True, null=True)
#     edate = models.DateTimeField(_(u'有効期間/終了'), blank=True, null=True)
#     detail = models.URLField(_(u'詳細URL'),blank=True, null=True)
#     money = models.IntegerField(_(u'ギフト金額'),default=0)
#     useterm_doc = models.TextField()
#     attention_doc = models.TextField()
    
class Applicants(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign,on_delete=models.CASCADE)
    win_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(_(u'Created Date At'), editable=False, auto_now_add=True, blank=True, null=True)
    
    def __str__(self):
        return self.campaign.title
    
class Plan(models.Model):
    name = models.CharField(_(u'プラン'),max_length=20, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    summary = models.CharField(max_length=50, blank=True, null=True)
    stripe_price_id = models.CharField(_(u'Stripe Products'),max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
class PaymentHistory(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    plan = models.ForeignKey(Plan,on_delete=models.CASCADE,blank=True, null=True)
    price = models.IntegerField(default=0)
    checkout_session = models.CharField(_(u'Stripe Subscriptions'),max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.user.email
    
    
@receiver(models.signals.post_delete, sender=Campaign)
def post_save_campaign_img(sender, instance, *args, **kwargs):
    """ Clean Old Image file """
    try:
        instance.missing_img.delete(save=False)        
    except:
        pass
    
@receiver(models.signals.pre_save, sender=Campaign)
def pre_save_campaign_img(sender, instance, *args, **kwargs):
    """ instance old image file will delete from os """
    try:
        old_img = instance.__class__.objects.get(id=instance.id).missing_img.path
        try:
            new_img = instance.missing_img.path
        except:
            new_img = None
        if new_img != old_img:            
            if os.path.exists(old_img):
                os.remove(old_img)
    except:
        pass
    
@receiver(models.signals.post_delete, sender=CreativeFile)
def post_save_creative_file(sender, instance, *args, **kwargs):
    """ Clean Old Image file """
    try:
        instance.file.delete(save=False)        
    except:
        pass
    
@receiver(models.signals.pre_save, sender=CreativeFile)
def pre_save_creative_file(sender, instance, *args, **kwargs):
    """ instance old image file will delete from os """
    try:
        old_img = instance.__class__.objects.get(id=instance.id).file.path
        try:
            new_img = instance.file.path
        except:
            new_img = None
        if new_img != old_img:            
            if os.path.exists(old_img):
                os.remove(old_img)
    except:
        pass
    
@receiver(models.signals.post_delete, sender=CampaignAction)
def post_save_campaignaction_tweet_img(sender, instance, *args, **kwargs):
    """ Clean Old Image file """
    try:
        instance.tweet_img.delete(save=False)        
    except:
        pass
    
@receiver(models.signals.pre_save, sender=CampaignAction)
def pre_save_creative_file(sender, instance, *args, **kwargs):
    """ instance old image file will delete from os """
    try:
        old_img = instance.__class__.objects.get(id=instance.id).tweet_img.path
        try:
            new_img = instance.tweet_img.path
        except:
            new_img = None
        if new_img != old_img:            
            if os.path.exists(old_img):
                os.remove(old_img)
    except:
        pass

@receiver(models.signals.post_delete, sender=DigitalGift)
def post_save_digitalgift_image(sender, instance, *args, **kwargs):
    """ Clean Old Image file """
    try:
        instance.image.delete(save=False)        
    except:
        pass
    
@receiver(models.signals.pre_save, sender=DigitalGift)
def pre_save_digitalgift_image(sender, instance, *args, **kwargs):
    """ instance old image file will delete from os """
    try:
        old_img = instance.__class__.objects.get(id=instance.id).image.path
        try:
            new_img = instance.image.path
        except:
            new_img = None
        if new_img != old_img:            
            if os.path.exists(old_img):
                os.remove(old_img)
    except:
        pass
