from django import template
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import User
from django.db.models import Count
from django.shortcuts import render, get_object_or_404

register = template.Library()
