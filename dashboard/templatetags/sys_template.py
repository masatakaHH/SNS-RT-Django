from django import template
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import User
from django.db.models import Count
from django.urls import reverse_lazy
from dashboard.models import Campaign,CreativeFile,CastTypeChoices,DigitalGift,CampaignAction,Applicants
from django.conf import settings
from datetime import datetime
import pytz

register = template.Library()
@register.filter
def campaign_url(campaign_id):    
    #campaign_url = reverse_lazy('dashboard:campaign-publish',kwargs={'campaign_id':campaign_id})
    campaign_url = settings.HOST_NAME + '/campaign/' + str(campaign_id)
    return campaign_url

@register.filter
def get_creative_img(campaign):
    try:
        creative_img = CreativeFile.objects.filter(campaign=campaign).first()
        return creative_img.file
    except:
        return None
    
@register.filter(is_safe=True)
def get_casttype(id):
    return CastTypeChoices[id-1][1]

@register.filter
def get_applicant_by_campaign(campaign):
    applicants = Applicants.objects.filter(campaign=campaign)
    return len(applicants)

@register.filter
def get_action_by_campaign(campaign):
    campaignactions = CampaignAction.objects.filter(campaign=campaign).first()
    return campaignactions

@register.filter
def get_digitalgift_by_campaign(campaign):
    gift = DigitalGift.objects.filter(campaign=campaign).first()    
    return gift

@register.filter
def check_status_campaign(campaign):
    now = datetime.today().astimezone(pytz.timezone('Asia/Tokyo'))
    if not campaign.is_publish:
        return '下書き'
    elif campaign.is_publish and campaign.sdate > now:
        return '公開待ち'
    elif campaign.is_publish and campaign.sdate < now and campaign.edate > now:
        return '公開中'
    elif campaign.is_publish and campaign.is_end:
        return '終了'
        