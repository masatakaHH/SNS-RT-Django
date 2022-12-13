from django.conf import settings
from django.db import models, transaction
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import datetime
import pytz
import uuid
import ulid
from accounts.models import User

class ULIDField(models.CharField):
    """ULIDフィールドの定義"""

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 8
        super(ULIDField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'char(8)'

class TwitterAction(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=256, blank=True, null=True)
    action_id = models.IntegerField(unique=True)
    
    def __str__(self):
        return self.name


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
        return obj.campaign.title

class CampaignAction(models.Model):
    campaign = models.ForeignKey(Campaign,on_delete=models.CASCADE)
    action_name = models.ForeignKey(TwitterAction,on_delete=models.CASCADE)
    twitter_id = models.CharField(max_length=20, blank=True, null=True)
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
    title = models.CharField(max_length=40)
    image = models.ImageField(upload_to="gift_files")
    codetype = models.CharField(_(u'コードタイプ'),max_length=40)
    candidate_num = models.IntegerField(_(u'当選者数'),default=1)
    color = models.CharField(_(u'ギフトカラー'),max_length=6)
    receipt_date = models.DateField(_(u'受取期限'), blank=True, null=True)
    sdate = models.DateTimeField(_(u'有効期間/開始'), blank=True, null=True)
    edate = models.DateTimeField(_(u'有効期間/終了'), blank=True, null=True)
    detail = models.URLField(_(u'詳細URL'),blank=True, null=True)
    money = models.IntegerField(_(u'ギフト金額'),default=0)
    useterm_doc = models.TextField()
    attention_doc = models.TextField()
    
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
    