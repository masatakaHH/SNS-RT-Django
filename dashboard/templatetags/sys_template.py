from django import template
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import User
from django.db.models import Count
from django.urls import reverse_lazy
from dashboard.models import Campaign
from django.conf import settings

register = template.Library()
@register.filter
def campaign_url(campaign_id):    
    #campaign_url = reverse_lazy('dashboard:campaign-publish',kwargs={'campaign_id':campaign_id})
    campaign_url = settings.HOST_NAME + '/' + str(campaign_id)
    return campaign_url