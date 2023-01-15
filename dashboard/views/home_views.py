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
from dashboard.models import Campaign,Applicants
from datetime import datetime
import pytz

class HomeView(TemplateView):
    model = User
    template_name = 'home.html'
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.today().astimezone(pytz.timezone('Asia/Tokyo'))
        publish_campaigns = []
        end_campaigns = []
        applicants = Applicants.objects.filter(user=self.request.user)
        for applicant in applicants:
            campaign = applicant.campaign
            if campaign.sdate < now:
                publish_campaigns.append(campaign)
            if campaign.edate < now:
                end_campaigns.append(campaign)
        
        context['publish_campaigns'] = publish_campaigns
        context['end_campaigns'] = end_campaigns
        #context['publish_campaigns'] = Campaign.objects.filter(user=self.request.user)
        #context['end_campaigns'] = Campaign.objects.filter(user=self.request.user)
        context['campaigns'] = Campaign.objects.filter(is_publish=True,sdate__lt=now).filter(edate__gt=now)
        
        return context
    
class TopPageView(TemplateView):
    model = User
    template_name = 'toppage.html'

class CampaignView(TemplateView):
    model = User
    template_name = 'campaign/campaign_publish.html'
    
    def get(self,request,campaign_id):
        now = datetime.today().astimezone(pytz.timezone('Asia/Tokyo'))
        campaign = get_object_or_404(Campaign, id=campaign_id)
        context = {}
        applicants = Applicants.objects.filter(user=request.user,campaign=campaign)
        if len(applicants) > 0:
            context['applied'] = True
        context['user'] = campaign.user       
        context['campaign'] = campaign
        return render(request,self.template_name,context)
    
class LegalView(TemplateView):
    template_name = 'legal.html'
    model = User
    
class AboutView(TemplateView):
    template_name = 'about.html'
    
class TermofServiceView(TemplateView):
    template_name = 'tos.html'
   