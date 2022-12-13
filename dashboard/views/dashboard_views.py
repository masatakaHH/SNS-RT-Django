from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404,reverse
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, View, TemplateView
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import User
from django.contrib.auth.decorators import user_passes_test
from io import BytesIO
from datetime import datetime
import pytz
from dashboard.models import Campaign,TwitterAction

class DashnoardView(LoginRequiredMixin,ListView):
    model = Campaign
    template_name = 'dashboard.html'
    
    def get_queryset(self):
        #campaigns = Campaign.objects.filter(user=request.user)
        #context['campaigns'] = campaigns
        return Campaign.objects.filter(user=self.request.user)
    
class CampaignDetail(LoginRequiredMixin,DetailView):
    model = Campaign
    template_name = 'campaign/detail.html'
    
    
class CampaignCreate(LoginRequiredMixin,TemplateView):
    model = Campaign
    template_name = 'campaign/create.html'
    
    def get(self,request):
        
        context = self.get_context_data(request)
        
        return render(request,self.template_name,context)
    
    def get_context_data(self, request, **kwargs):
        casttype = request.GET.get('casttype')        
        context = super().get_context_data(**kwargs)
        
        context['casttype'] = casttype
        context['twitter_actions'] = TwitterAction.objects.all()
        return context
    
    def post(self,request):
        casttype = request.POST.get('casttype')   
        basic_name = request.POST.get('basic_name')
        basic_context = request.POST.get('basic_context')
        publish_date = request.POST.get('publish_date')
        publish_date_time = request.POST.get('publish_date_time')
        
        end_date = request.POST.get('end_date')
        end_date_time = request.POST.get('end_date_time')
        twitter_action_id = request.POST.get('twitter_action_id')
        gift_data_set = request.POST.get('gift_data_set')
        if casttype == 1:
            instant_draw_value = request.POST.get('instant_draw_value')
        
        if publish_date and publish_date_time:
            publish_date = datetime.strptime(publish_date,'%Y-%m-%d')
            publish_date_time = datetime.strptime(publish_date_time,'%H:%M').time()
            publish_dtime = datetime.combine(publish_date,publish_date_time)
        
        if end_date and end_date_time:
            end_date = datetime.strptime(end_date,'%Y-%m-%d')
            end_date_time = datetime.strptime(end_date_time,'%H:%M').time()
            end_dtime = datetime.combine(end_date,end_date_time)
            print(end_dtime)
            if end_dtime < datetime.today():
                print('終了日付入力が無効です。')
                messages.add_message(request, messages.ERROR, '正しい終了日付を入力してください。')
                return JsonResponse({'status':'failed'})        
        
        campaign = Campaign.objects.create(user=request.user,casttype=casttype,title=basic_name,context=basic_context)
        if publish_date and publish_date_time: campaign.sdate = publish_dtime
        if end_date and end_date_time: campaign.edate = end_dtime
        if casttype == 1: campaign.instancewin = instant_draw_value
        campaign.save()
        
        return JsonResponse({'status':'success'})
    
class CampaignUpdate(LoginRequiredMixin,TemplateView):
    model = Campaign
    template_name = 'campaign/edit.html'
    
    def get(self,request,campaign_id):        
        context = {}
        context['object'] = Campaign.objects.get(id=campaign_id)
        context['twitter_actions'] = TwitterAction.objects.all()
        return render(request,self.template_name,context)
    
def campaign_update(request):
    campaign_id = request.POST.get('campaign_id')
    campaign = get_object_or_404(Campaign,id=campaign_id)
    basic_name = request.POST.get('basic_name')
    basic_context = request.POST.get('basic_context')
    publish_date = request.POST.get('publish_date')
    publish_date_time = request.POST.get('publish_date_time')
    end_date = request.POST.get('end_date')
    end_date_time = request.POST.get('end_date_time')
    twitter_action_id = request.POST.get('twitter_action_id')
    gift_data_set = request.POST.get('gift_data_set')
    if campaign.casttype == 1:
        instant_draw_value = request.POST.get('instant_draw_value')
        
    return JsonResponse({'status':'success'})
        