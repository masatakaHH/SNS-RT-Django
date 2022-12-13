from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.shortcuts import render, get_object_or_404

register = template.Library()


