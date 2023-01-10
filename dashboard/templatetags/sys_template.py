from django import template
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import User
from django.db.models import Count
from django.urls import reverse_lazy
from dashboard.models import Campaign,CreativeFile,CastTypeChoices,DigitalGift,CampaignAction,Applicants
from django.conf import settings

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
