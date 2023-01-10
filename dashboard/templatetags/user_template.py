from django import template
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import User
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.urls import reverse_lazy

register = template.Library()
@register.filter
def get_profile_url(username):    
    profile_url = reverse_lazy('accounts:profile-publish',kwargs={'pk':username})
    profile_url = settings.HOST_NAME + profile_url
    return profile_url

