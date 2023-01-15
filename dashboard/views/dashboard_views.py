from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404,reverse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, View, TemplateView, DeleteView
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import User,TwitterUser
from django.contrib.auth.decorators import user_passes_test
from io import BytesIO
from datetime import datetime
from twitter_api.twitter_api import TwitterAPI
from accounts.models import TwitterAuthToken, TwitterUser
from dashboard.models import Campaign,TwitterAction,CreativeFile,CampaignAction,DigitalGift,Applicants
from django.conf import settings
import requests
import pytz
import json

class DashnoardView(LoginRequiredMixin,ListView):
    model = Campaign
    template_name = 'dashboard.html'
    
    def get_queryset(self):
        #campaigns = Campaign.objects.filter(user=request.user)
        queryset = Campaign.objects.filter(user=self.request.user).order_by('-created_at')
        now = datetime.today().astimezone(pytz.timezone('Asia/Tokyo'))
        if self.request.GET.get('status'):
            status = self.request.GET.get('status')
            self.request.session['status'] = status
            if status == 'draft':
                queryset = queryset.filter(is_publish=False,is_end=False)
            elif status == 'ready':
                queryset = queryset.filter(is_publish=True,is_end=False).filter(sdate__lt=now)
            elif status == 'published':
                queryset = queryset.filter(is_publish=True,is_end=False).filter(sdate__gt=now)
            elif status == 'closed':
                queryset = queryset.filter(is_publish=True,is_end=True)
        else:
            self.request.session['status'] = ''
        return queryset
    
class CampaignDetail(LoginRequiredMixin,DetailView):
    model = Campaign
    template_name = 'campaign/detail.html'
    
    def get(self,request,pk):
        context = {}        
        context['object'] = get_object_or_404(Campaign,id=pk)
        context['creativefiles'] = CreativeFile.objects.filter(campaign_id=pk)
        context['digitalgifts'] = DigitalGift.objects.filter(campaign_id=pk)
        context['campaignactions'] = CampaignAction.objects.filter(campaign_id=pk)
        return render(request,self.template_name,context)

@login_required
def campaign_delete(request,pk):
    obj = get_object_or_404(Campaign,id=pk)
    obj.delete()
    return redirect('dashboard:dashboardview')
    
    
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
        action_list = request.POST.get('action_list')        
        action_list = json.loads(action_list)
        
        gift_data_set = request.POST.get('gift_data_set')
        gift_data_set = json.loads(gift_data_set)
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
            if end_dtime < datetime.today():
                print('終了日付入力が無効です。')
                #messages.add_message(request, messages.ERROR, '正しい終了日付を入力してください。')
                return JsonResponse({'status':'failed'})        
        
        campaign = Campaign.objects.create(user=request.user,casttype=casttype,title=basic_name,context=basic_context)
        if publish_date and publish_date_time: campaign.sdate = publish_dtime
        if end_date and end_date_time: campaign.edate = end_dtime
        if casttype == 1: campaign.instancewin = instant_draw_value
        campaign.save()
        
        if 'instance_missing_img_file' in request.FILES:
            instance_missing_img_file = request.FILES.get('instance_missing_img_file')        
            campaign.missing_img = instance_missing_img_file
            campaign.save()
        
        if 'creative_image_file' in request.FILES:
            creative_image_file = request.FILES.get('creative_image_file')
            print(creative_image_file)
            creative_file = CreativeFile.objects.create(campaign=campaign,file=creative_image_file)
        
        if len(action_list) > 0:
            for action_list_item in action_list:
                action_list_item = json.dumps(action_list_item)
                action_list_item = json.loads(action_list_item)
                action_id = int(action_list_item['action_id'])
                action_target = action_list_item['action_target']
                try:
                    twitteraction = TwitterAction.objects.get(action_id=action_id)
                    campaign_action = CampaignAction.objects.create(campaign=campaign,action_name=twitteraction)
                    if action_id == 1:
                        campaign_action.screen_name = action_target
                    elif action_id == 2:
                        campaign_action.retweet_url = action_target
                    campaign_action.save()
                except:                    
                    return JsonResponse({'status':'campaign_action'})
        
        
        if len(gift_data_set) > 0:
            print(gift_data_set['gift_name'])
            digitalgift = DigitalGift.objects.create(campaign=campaign)
            digitalgift.title = gift_data_set['gift_name']
            digitalgift.codetype = gift_data_set['gift_code']
            digitalgift.candidate_num = gift_data_set['giftapplicant']
            digitalgift.receipt_date = gift_data_set['gift_receive_limit_date']
            
            gift_effect_start_date = gift_data_set['gift_effect_start_date']
            gift_effect_start_date_time = gift_data_set['gift_effect_start_date_time']
            gift_effect_start_date = datetime.strptime(gift_effect_start_date,'%Y-%m-%d')
            gift_effect_start_date_time = datetime.strptime(gift_effect_start_date_time,'%H:%M').time()
            gift_effect__sdate = datetime.combine(gift_effect_start_date,gift_effect_start_date_time)
            digitalgift.sdate = gift_effect__sdate
            
            gift_effect_end_date = gift_data_set['gift_effect_end_date']
            gift_effect_end_date_time = gift_data_set['gift_effect_end_date_time']
            gift_effect_end_date = datetime.strptime(gift_effect_end_date,'%Y-%m-%d')
            gift_effect_end_date_time = datetime.strptime(gift_effect_end_date_time,'%H:%M').time()
            gift_effect__edate = datetime.combine(gift_effect_end_date,gift_effect_end_date_time)
            digitalgift.edate = gift_effect__edate
            
            digitalgift.money = gift_data_set['gift_price']
            digitalgift.detail = gift_data_set['gift_detail_url']
            digitalgift.useterm_doc = gift_data_set['gift_userterm']
            digitalgift.save()
            
            if 'gift_image_file' in request.FILES:
                gift_image_file = request.FILES.get('gift_image_file')            
                digitalgift.image = gift_image_file
                digitalgift.save()
        
        return JsonResponse({'status':'success'})
    
class CampaignUpdate(LoginRequiredMixin,TemplateView):
    model = Campaign
    template_name = 'campaign/edit.html'
    
    def get(self,request,campaign_id):        
        context = {}
        context['object'] = Campaign.objects.get(id=campaign_id)
        context['creativefiles'] = CreativeFile.objects.filter(campaign_id=campaign_id)
        context['digitalgift'] = DigitalGift.objects.filter(campaign_id=campaign_id).first()
        context['campaignactions'] = CampaignAction.objects.filter(campaign_id=campaign_id)
        context['twitter_actions'] = TwitterAction.objects.all()
        return render(request,self.template_name,context)
    
    def post(self,request,campaign_id):
        campaign = get_object_or_404(Campaign,id=campaign_id)
        print(campaign)
        casttype = campaign.casttype
        basic_name = request.POST.get('basic_name')
        basic_context = request.POST.get('basic_context')
        publish_date = request.POST.get('publish_date')
        publish_date_time = request.POST.get('publish_date_time')        
        end_date = request.POST.get('end_date')
        end_date_time = request.POST.get('end_date_time')
        action_list = request.POST.get('action_list')
        action_list = json.loads(action_list)        
        gift_data_set = request.POST.get('gift_data_set')
        gift_data_set = json.loads(gift_data_set)
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
            if end_dtime < datetime.today():
                print('終了日付入力が無効です。')
                #messages.add_message(request, messages.ERROR, '正しい終了日付を入力してください。')
                return JsonResponse({'status':'failed'})   
        campaign.title = basic_name
        campaign.context = basic_context  
        if publish_date and publish_date_time: campaign.sdate = publish_dtime
        if end_date and end_date_time: campaign.edate = end_dtime
        if casttype == 1: campaign.instancewin = instant_draw_value
        if 'instance_missing_img_file' in request.FILES:
            instance_missing_img_file = request.FILES.get('instance_missing_img_file')        
            campaign.missing_img = instance_missing_img_file
            campaign.save()
        
        if 'creative_image_file' in request.FILES:
            creative_image_file = request.FILES.get('creative_image_file')
            print(creative_image_file)
            try:
                creative_file = CreativeFile.objects.filter(campaign=campaign)
                creative_file.delete()
            except:
                pass
            creative_file = CreativeFile.objects.create(campaign=campaign,file=creative_image_file)
        
        if len(action_list) > 0:
            for action_list_item in action_list:
                action_list_item = json.dumps(action_list_item)
                action_list_item = json.loads(action_list_item)
                campaign_action_id = int(action_list_item['campaign_action_id'])
                action_id = int(action_list_item['action_id'])
                action_target = action_list_item['action_target']
                try:
                    twitteraction = TwitterAction.objects.get(action_id=action_id)
                    if campaign_action_id > 0:
                        campaign_action = get_object_or_404(CampaignAction,id=campaign_action_id)
                    else:
                        campaign_action = CampaignAction.objects.create(campaign=campaign,action_name=twitteraction)
                    
                    if action_id == 1:
                        campaign_action.screen_name = action_target
                    elif action_id == 2:
                        campaign_action.retweet_url = action_target
                    campaign_action.save()
                except:                    
                    return JsonResponse({'status':'campaign_action'})
        else:
            try:
                campaign_action = CampaignAction.objects.filter(campaign=campaign)
                campaign_action.delete()
            except:
                pass
                
        if gift_data_set != '':
            digitalgift_id = gift_data_set['digitalgift_id']
            if digitalgift_id != '':
                digitalgift = get_object_or_404(DigitalGift,id=digitalgift_id)
            else:
                digitalgift = DigitalGift.objects.create(campaign=campaign)
            digitalgift.title = gift_data_set['gift_name']
            digitalgift.codetype = gift_data_set['gift_code']
            digitalgift.candidate_num = gift_data_set['giftapplicant']
            digitalgift.receipt_date = gift_data_set['gift_receive_limit_date']
            
            gift_effect_start_date = gift_data_set['gift_effect_start_date']
            gift_effect_start_date_time = gift_data_set['gift_effect_start_date_time']
            gift_effect_start_date = datetime.strptime(gift_effect_start_date,'%Y-%m-%d')
            gift_effect_start_date_time = datetime.strptime(gift_effect_start_date_time,'%H:%M').time()
            gift_effect__sdate = datetime.combine(gift_effect_start_date,gift_effect_start_date_time)
            digitalgift.sdate = gift_effect__sdate
            
            gift_effect_end_date = gift_data_set['gift_effect_end_date']
            gift_effect_end_date_time = gift_data_set['gift_effect_end_date_time']
            gift_effect_end_date = datetime.strptime(gift_effect_end_date,'%Y-%m-%d')
            gift_effect_end_date_time = datetime.strptime(gift_effect_end_date_time,'%H:%M').time()
            gift_effect__edate = datetime.combine(gift_effect_end_date,gift_effect_end_date_time)
            digitalgift.edate = gift_effect__edate
            
            digitalgift.money = gift_data_set['gift_price']
            digitalgift.detail = gift_data_set['gift_detail_url']
            digitalgift.useterm_doc = gift_data_set['gift_userterm']
            digitalgift.save()
            
            if 'gift_image_file' in request.FILES:
                gift_image_file = request.FILES.get('gift_image_file')            
                digitalgift.image = gift_image_file
                digitalgift.save()
        else:
            try:
                obj = DigitalGift.objects.filter(campaign=campaign)
                obj.delete()
            except:
                pass
        
        campaign.save()
        
        return JsonResponse({'status':'success'})

@login_required
def campaign_publish(request,pk):
    campaign = get_object_or_404(Campaign,id=pk)
    publish_date = request.POST.get('publish_date')
    publish_date_time = request.POST.get('publish_date_time')
    end_date = request.POST.get('end_date')
    end_date_time = request.POST.get('end_date_time')
    if publish_date and publish_date_time:
        publish_date = datetime.strptime(publish_date,'%Y-%m-%d')
        publish_date_time = datetime.strptime(publish_date_time,'%H:%M').time()
        publish_dtime = datetime.combine(publish_date,publish_date_time)
    
    if end_date and end_date_time:
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
        end_date_time = datetime.strptime(end_date_time,'%H:%M').time()
        end_dtime = datetime.combine(end_date,end_date_time)            
        if end_dtime < datetime.today():
            print('終了日付入力が無効です。')
            messages.add_message(request, messages.ERROR, '正しい終了日付を入力してください。')
            return redirect('dashboard:campaign-detail', pk=pk)
    
    if publish_date and publish_date_time: campaign.sdate = publish_dtime
    if end_date and end_date_time: 
        campaign.edate = end_dtime
        campaign.is_publish = True
    campaign.save()
    return redirect('dashboard:campaign-detail', pk=pk)
     
@login_required
def gift_update(request):
    try:
        gift_id = request.POST.get('gift_id')
        campaign_id = request.POST.get('campaign_id')
        digitalgift = get_object_or_404(DigitalGift,id=gift_id)
        #gift_data_set = request.POST.get('gift_data_set')
        #gift_data_set = json.loads(gift_data_set)
        
        digitalgift.title = request.POST.get('giftname')
        digitalgift.codetype = request.POST.get('giftcode')
        digitalgift.candidate_num = request.POST.get('giftapplicant')
        digitalgift.receipt_date = request.POST.get('gift_receive_limit_date')
        
        gift_effect_start_date = request.POST.get('gift_effect_start_date')
        gift_effect_start_date_time = request.POST.get('gift_effect_start_date_time')
        gift_effect_start_date = datetime.strptime(gift_effect_start_date,'%Y-%m-%d')
        gift_effect_start_date_time = datetime.strptime(gift_effect_start_date_time,'%H:%M').time()
        gift_effect__sdate = datetime.combine(gift_effect_start_date,gift_effect_start_date_time)
        digitalgift.sdate = gift_effect__sdate
        
        gift_effect_end_date = request.POST.get('gift_effect_end_date')
        gift_effect_end_date_time = request.POST.get('gift_effect_end_date_time')
        gift_effect_end_date = datetime.strptime(gift_effect_end_date,'%Y-%m-%d')
        gift_effect_end_date_time = datetime.strptime(gift_effect_end_date_time,'%H:%M').time()
        gift_effect__edate = datetime.combine(gift_effect_end_date,gift_effect_end_date_time)
        digitalgift.edate = gift_effect__edate
        
        digitalgift.money = request.POST.get('gift_price')
        digitalgift.detail = request.POST.get('gift_detail_url')
        digitalgift.useterm_doc = request.POST.get('gift_userterm')
        digitalgift.save()
       
        if 'giftimg' in request.FILES:
            gift_image_file = request.FILES.get('giftimg')                 
            digitalgift.image = gift_image_file
            digitalgift.save()
            
        return redirect('dashboard:campaign-detail', pk=campaign_id)
    except:
        print("failed")
        return redirect('dashboard:dashboardview',pk=campaign_id)

def applicant(request):
    if request.user.is_authenticated:
        campaign_id = request.POST.get('campaign_id')
        campaign = Campaign.objects.get(id=campaign_id)
        return JsonResponse({'success':'True'})
    else:
        return JsonResponse({'success':'login'})

class ApplicantPush(TemplateView):
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
    
    def post(self,request):
        if request.user.is_authenticated:
            try:
                twitter_user = TwitterUser.objects.get(user=request.user)
            except:
                return JsonResponse({'status':'twitter'})
            campaign_id = request.POST.get('campaign_id')
            campaign_action_id = request.POST.get('campaign_action')
            campaign = Campaign.objects.get(id=campaign_id)
            campaignaction = CampaignAction.objects.get(id=campaign_action_id)
            #check_result = check_twitter(twitter_user,campaignaction)
            response = follow_retweet(twitter_user,campaignaction)
            if response:
                applicants = Applicants.objects.filter(user=request.user,campaign=campaign)
                if len(applicants) == 0:
                    applicant = Applicants.objects.create(user=request.user,campaign=campaign)
                    print(applicant)
                else:
                    return JsonResponse({'status':'applied'})
                return JsonResponse({'status':'success'})
            else:
                return JsonResponse({'status':'twitter'})
        else:
            return JsonResponse({'status':'login'})
        
def follow_retweet(twitter_user,campaignaction):
    twitter_api = TwitterAPI()
    twitter_auth_token = get_object_or_404(TwitterAuthToken, id=twitter_user.twitter_oauth_token.id)
    client = twitter_api.client_init(twitter_auth_token.oauth_token, twitter_auth_token.oauth_token_secret)
    twitter_id = twitter_user.twitter_id
    if campaignaction.action_name.name == 'フォロー':
        twitter_screenname = campaignaction.screen_name
        twitter_user_id = get_userid_by_username(twitter_screenname)
        #print(twitter_user_id)
        try:
            response = client.follow_user(target_user_id=twitter_user_id,user_auth=True)
            return True
        except:
            return False
    if campaignaction.action_name.name == 'リツイート':
        retweet_url = campaignaction.retweet_url
        tweet_id = retweet_url.split('/')[-1]
        try:
            response = client.retweet(tweet_id=tweet_id,user_auth=True)
            print(response)
            return True
        except:
            return False

def check_twitter(twitter_user,campaignaction):
    twitter_api = TwitterAPI()
    twitter_auth_token = get_object_or_404(TwitterAuthToken, id=twitter_user.twitter_oauth_token.id)
    client = twitter_api.client_init(twitter_auth_token.oauth_token, twitter_auth_token.oauth_token_secret)    
    max_results = 1000
    twitter_id = twitter_user.twitter_id
    global has_next_page_1
    global next_token
    global retweet_next_page
    global retweet_next_token
    has_next_page_1 = True
    retweet_next_page= True
    next_token = None
    retweet_next_token = None
    following_infos = [] 
    if campaignaction.action_name.name == 'フォロー':
        twitter_screenname = campaignaction.screen_name
        while True:
            if has_next_page_1:
                following_info = get_users_following_loop(twitter_api,twitter_id,client,max_results)                
                following_infos.append(following_info[0])
            else:
                break
                
        for following_info in following_infos:
            for one in following_info:            
                if twitter_screenname == one.username:
                    return True
    retweets_infos = [] 
    if campaignaction.action_name.name == 'リツイート':
        retweet_url = campaignaction.retweet_url
        tweet_id = retweet_url.split('/')[-1]
        retweet_info = get_users_retweet_loop(tweet_id)
        print(retweet_info['data'])
        # while True:
        #     if retweet_next_page:
        #         retweet_info = get_users_retweet_loop(tweet_id)                
        #         retweets_infos.append(retweet_info['data'])
        #     else:
        #         break
        # for retweets_info in retweets_infos:
        #     for one in retweets_info:         
        #         print(one.id)
        #         if twitter_id == one.id:
        #             return True
    return False
           
    
def get_users_following_loop(twitter_api,twitter_id,client,max_results):
    global has_next_page_1
    global next_token
    if next_token is None:
        following_info = twitter_api.get_users_following_ids(twitter_id,client,max_results)
    else:
        following_info = twitter_api.get_users_following_ids(twitter_id,client,max_results,next_token)
    try:        
        next_token = following_info[3]['next_token']
    except:
        has_next_page_1 = False
    
    return following_info

def get_users_retweet_loop(tweet_id):
    global retweet_next_page
    global retweet_next_token
    
    #id = "1354143047324299264"    
    max_results = "max_results=100"
    url = "https://api.twitter.com/2/tweets/{}/retweeted_by".format(tweet_id)
    if retweet_next_token is None:
        response = requests.request("GET", url, auth=bearer_oauth, params=max_results)
    else:
        pagination_token = "pagination_token={}".format(retweet_next_token)
        response = requests.request("GET", url, auth=bearer_oauth, params=pagination_token)
    retweets = response.json()
    #retweets = json.dumps(retweets)
    
    try:
        retweet_next_token = retweets['meta']['next_token']
        retweet_next_page = True
    except:        
        retweet_next_page = False
    
    return retweets

def get_userid_by_username(username):
    url = "https://api.twitter.com/2/users/by/username/{}".format(username)
    response = requests.request("GET", url, auth=bearer_oauth)
    user = response.json()
    return user['data']['id']
    
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    bearer_token = settings.BEARER_TOKEN
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RetweetedByPython"
    return r