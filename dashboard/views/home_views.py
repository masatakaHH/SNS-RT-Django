from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404,reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse,JsonResponse
from accounts.models import User
from django.contrib.auth.decorators import user_passes_test

class HomeView(TemplateView):
    model = User
    template_name = 'home.html'
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)
        return context

class CampaignView(TemplateView):
    model = User
    template_name = 'home.html'