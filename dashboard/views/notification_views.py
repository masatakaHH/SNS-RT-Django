from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404,reverse
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, View, TemplateView
from django.http import HttpResponse,JsonResponse
from accounts.models import User
from django.contrib.auth.decorators import user_passes_test

