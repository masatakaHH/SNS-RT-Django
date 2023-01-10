from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, HttpResponseRedirect, HttpResponse, get_object_or_404
from django.http import JsonResponse
from .decorators import twitter_login_required
from django.contrib.auth.decorators import user_passes_test
from .models import TwitterAuthToken, TwitterUser
from .authorization import create_update_user_from_twitter, check_token_still_valid,connect_twitter_to_user
from twitter_api.twitter_api import TwitterAPI
from django.views.generic import ListView, DetailView, View, TemplateView, CreateView
from django.views.generic.edit import UpdateView
from accounts.models import User,Profile
from django.contrib.auth import views as auth_views
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import PasswordChangeForm,SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserCreateForm, ProfiledAuthenticationForm, UserUpdateForm, PaymentForm
from urllib.parse import urlencode
from core.utils import id_generator
from django.conf import settings
from dashboard.models import PaymentHistory,Plan, Campaign, Applicants
import stripe
import calendar
import time
from datetime import datetime
import pytz

stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.
class LoginView(View):
    template_name = "registration/login.html"
    form_class = ProfiledAuthenticationForm
    
    def get_success_url(self):
        return reverse('dashboard:toppage')
    
    def get(self, request, *args, **kwargs):
        
        context = {'form': self.form_class()}
        if self.request.user.is_authenticated:
            return render(request, 'home.html')
        else:
            return render(request,self.template_name,context)
        
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)                
                return HttpResponseRedirect(self.get_success_url())

        return render(request, self.template_name, {'form': form})

class Signup(View):
    redirect_authenticated_user = True
    form_class = UserCreateForm
    template_name = 'registration/signup.html'
    
    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, 'Your account was created successfully! Please log in to continue.')
        
        if self.request.GET.get("next", None):
            return reverse('accounts:login') + "?" + urlencode({"next": self.request.GET.get('next')})
        return reverse('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:toppage')
        return super(Signup, self).dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        context = {'form': self.form_class()}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():            
            user = form.save()
            return HttpResponseRedirect(self.get_success_url())

        return render(request, self.template_name, {'form': form})
        
@login_required
def logout_user(request):
    logout(request)
    return redirect('dashboard:toppage')

def twitter_login(request):
    twitter_api = TwitterAPI()
    url, oauth_token, oauth_token_secret = twitter_api.twitter_login()
    if url is None or url == '':
        messages.add_message(request, messages.ERROR, 'Unable to login. Please try again.')
        return render(request, 'registration/error_page.html')
    else:
        twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
        if twitter_auth_token is None:
            twitter_auth_token = TwitterAuthToken(oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
            twitter_auth_token.save()
        else:
            twitter_auth_token.oauth_token_secret = oauth_token_secret
            twitter_auth_token.save()
        return redirect(url)


def twitter_callback(request):
    if 'denied' in request.GET:
        messages.add_message(request, messages.ERROR, 'Unable to login or login canceled. Please try again.')
        return render(request, 'registration/error_page.html')
    twitter_api = TwitterAPI()
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_token = request.GET.get('oauth_token')
    twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
    if twitter_auth_token is not None:
        access_token, access_token_secret = twitter_api.twitter_callback(oauth_verifier, oauth_token, twitter_auth_token.oauth_token_secret)
        if access_token is not None and access_token_secret is not None:
            twitter_auth_token.oauth_token = access_token
            twitter_auth_token.oauth_token_secret = access_token_secret
            twitter_auth_token.save()
            # Create user
            #client = twitter_api.client_init(access_token, access_token_secret)
            #info = twitter_api.get_me(client)
            api = twitter_api.api_init(access_token, access_token_secret)
            info1 = api.verify_credentials(include_email=True)
            #print(info1.id)
            if info1 is not None:
                #twitter_user_new = TwitterUser(twitter_id=info[0]['id'], screen_name=info[0]['username'],name=info[0]['name'], profile_image_url=info[0]['profile_image_url'])
                twitter_user_new = TwitterUser(twitter_id=info1.id, screen_name=info1.screen_name,name=info1.name, profile_image_url=info1.profile_image_url)
                twitter_user_new.twitter_oauth_token = twitter_auth_token
                if request.user.is_authenticated:
                    twitter_user = connect_twitter_to_user(twitter_user_new,request.user)
                    if request.GET.get('next'):
                        return redirect(request.GET.get('next'))
                    else:
                        return redirect('accounts:profile')
                else:
                    user, twitter_user = create_update_user_from_twitter(twitter_user_new,info1.email)
                    if user is not None:
                        login(request, user)
                        return redirect('dashboard:toppage')
            else:
                messages.add_message(request, messages.ERROR, 'Unable to get profile details. Please try again.')
                return render(request, 'registration/error_page.html')
        else:
            messages.add_message(request, messages.ERROR, 'Unable to get access token. Please try again.')
            return render(request, 'registration/error_page.html')
    else:
        messages.add_message(request, messages.ERROR, 'Unable to retrieve access token. Please try again.')
        return render(request, 'registration/error_page.html')

@login_required
def twitter_logout(request):
    try:
        twitteruser = TwitterUser.objects.get(user=request.user)
        twitteruser.delete()
    except:
        pass
    return redirect('accounts:profile')


class UserDetailView(LoginRequiredMixin,TemplateView):
    model = User
    template_name = 'user/user_detail.html'
    
    def get(self,request):
        
        context = {}
        context['user'] = request.user
        try:
            twitteruser = TwitterUser.objects.get(user=request.user)
            context['twitteruser'] = twitteruser
        except TwitterUser.DoesNotExist:
            pass
        if 'pw_form' not in context:
            context['pw_form'] = SetPasswordForm(user=self.request.user)
        return render(request,self.template_name,context)
    
@login_required
def update_profile(request):
    username = request.POST.get('username')
    if username == request.user.username:
        pass
    else:
        try:
            user = User.objects.get(username=username)
            messages.add_message(request, messages.ERROR, '既にこのユーザー名は存在する為、登録できません。')
            return redirect(reverse("accounts:profile"))
        except User.DoesNotExist:
            user = request.user
            user.username = username
            user.save()
    
    owner_name = request.POST.get('owner_name')
    account_name = request.POST.get('account_name')
    brand_name = request.POST.get('brand_name')    
    contact_form = request.POST.get('contact_form')
    contact_form_email = request.POST.get('contact_form_email')
    profile = Profile.objects.get(user=request.user)
    profile.owner_name = owner_name
    profile.account_name = account_name
    profile.brand_name = brand_name
    profile.contact_form = contact_form
    profile.contact_form_email = contact_form_email
    profile.save()
    if 'header_img' in request.FILES:
        header_img = request.FILES.get('header_img')
        profile.header_img = header_img
        profile.save()
    
    return redirect(reverse("accounts:profile"))

@login_required
def change_email(request):
    new_email = request.POST.get('new_email')    
    try:
        user = User.objects.get(email=new_email)
        messages.add_message(request, messages.ERROR, '既にこのメールは存在する為、登録できません。')
        return JsonResponse({"success":"failed"})
    except User.DoesNotExist:
        pass
    user = request.user
    user.email = new_email
    user.save()
    messages.add_message(request, messages.SUCCESS, '成功！')
    return JsonResponse({'status':'success'})

@login_required
def change_password(request):
    pw_form = SetPasswordForm(user=request.user, data=request.POST)
    ctxt = {}
    if pw_form.is_valid():
        print("pw_form is valid")
        messages.add_message(request, messages.SUCCESS, '成功！')
        pw_form.save()
        update_session_auth_hash(request, pw_form.user)                
    else:
        print(pw_form.errors)
        messages.add_message(request, messages.ERROR, 'ERROR')
        ctxt['pw_form'] = pw_form
    
    return redirect('accounts:profile')    

@login_required
def update_user_photo(request):
    pk = request.POST.get('id')
    user = get_object_or_404(User,id=pk)
    if 'user_avatar' in request.FILES:
        avatar = request.FILES.get('user_avatar')
        user.avatar = avatar
        user.save()
        return JsonResponse({'success':True})

class ProfilePublishView(TemplateView):
    model = User
    template_name = 'user/profile.html'
    
    def get(self,request,pk):        
        now = datetime.today().astimezone(pytz.timezone('Asia/Tokyo'))
        user = get_object_or_404(User, username=pk)
        context = {}
        context['user'] = user
        try:
            twitter_user = TwitterUser.objects.get(user=user)
            context['twitter_user'] = twitter_user
        except:
            pass
        campaigns = Campaign.objects.filter(user=user)
        context['campaign_num'] = len(campaigns)
        applicant_nums = 0
        for campaign in campaigns:
            applicant_num = len(Applicants.objects.filter(campaign=campaign))
            applicant_nums += applicant_num
        context['applicant_num'] = applicant_nums
        #context['publish_campaigns'] = campaigns.filter(is_publish=True,is_end=False).filter(sdate__gt=now)
        context['publish_campaigns'] = campaigns
        #context['end_campaigns'] = campaigns.filter(is_publish=True,is_end=True).filter(edate__gt=now)
        context['end_campaigns'] = campaigns
        return render(request,self.template_name,context)

class PlanView(TemplateView):
    model = Plan
    template_name = 'payment/pricing.html'
    
    def get(self,request):
        context = {}
        plans = Plan.objects.all()
        paymenthistory = PaymentHistory.objects.get(user=request.user)
        context['plans'] = plans
        context['paymenthistory'] = paymenthistory
        return render(request, self.template_name, context)
    
class CardView(TemplateView):
    model = User
    template_name = 'payment/card.html'
    
    def get(self, request, *args, **kwargs):
        context = {            
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
        }
        userprofile = self.request.user.profile
        if userprofile.stripe_customer_id:
            # fetch the users card list
            cards = stripe.Customer.list_sources(
                userprofile.stripe_customer_id,
                limit=3,
                object='card'
            )
            card_list = cards['data']
            if len(card_list) > 0:
                # update the context with the default card
                context.update({
                    'card': card_list[0]
                })
                print(card_list[0])
        return render(self.request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = PaymentForm(self.request.POST)
        userprofile = Profile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:               

                customer = stripe.Customer.modify(
                    userprofile.stripe_customer_id,
                    card=token
                )
                userprofile.stripe_customer_id = customer['id']
                userprofile.save()

            else:
                customer = stripe.Customer.create(
                    email=self.request.user.email,
                    card=token
                )
                # customer.sources.create(source=token)
                userprofile.stripe_customer_id = customer['id']                
                userprofile.save()
            return redirect("accounts:payment")
        else:
            return redirect("accounts:payment")
        
@login_required
def payment_history(request):
    payment_history = PaymentHistory.objects.filter(user=request.user)
    return render(request, 'payment/payment_history.html', context={'payment_history':payment_history})

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLIC_KEY}
        return JsonResponse(stripe_config, safe=False)

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        plan_id = request.GET.get('plan_id')
        plan = get_object_or_404(Plan, id=plan_id)
        user = request.user        
        #domain_url = 'http://127.0.0.1:8003/'
        domain_url = request.scheme+'://'+request.META['HTTP_HOST']+'/'
        if request.user.email == '':
            messages.add_message(request, messages.SUCCESS, 'メールアドレスをご記入ください！')
            email = 'example@domain.com'
            return JsonResponse({'email': 'error'})
        else:
            email = request.user.email
        print(request.user.email)
        dt = time.gmtime()        
        ts = calendar.timegm(dt)        
        timestamp_delta = ts + 14 * 24 * 60 * 60 + 9 * 60 * 60
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            payment_history = PaymentHistory.objects.get(user=user)        
            subscription_id = payment_history.checkout_session
            if subscription_id:
                stripe.Subscription.delete(subscription_id)
        except:
            pass
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'accounts/payment/success?session_id={CHECKOUT_SESSION_ID}&plan_id='+str(plan_id),
                cancel_url=domain_url + 'payment',
                payment_method_types=['card'],
                customer_email=email,
                mode='subscription',
                locale='ja',
                line_items=[
                    {
                        'price': plan.stripe_price_id,
                        "quantity": 1,
                    }
                ],
                
                metadata={'plan_id':plan_id},
                subscription_data={
                    'trial_end':int(timestamp_delta)
                },
                client_reference_id = request.user.id
            )            
            
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)})

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    print(event)
    if event['type'] == 'checkout.session.completed':

        data = event['data']['object']
        user_id = data['client_reference_id']
        user = User.objects.get(id=user_id)
        plan_id = int(data['metadata']['plan_id'])
    return HttpResponse(status=200)

class SuccessView(TemplateView):
    template_name = 'payment/payment_success.html'

    def get(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session_id = request.GET.get('session_id')        
        stripe_response = stripe.checkout.Session.retrieve(
            session_id,
            expand=['subscription']
        )
        print(stripe_response['subscription']['id'])
        plan_id = request.GET.get('plan_id')
        plan = get_object_or_404(Plan, id=plan_id)
        try:
            payment_history = PaymentHistory.objects.get(user=request.user)            
        except:
            payment_history = PaymentHistory()        
            payment_history.user = request.user
        payment_history.plan_id = plan_id
        payment_history.price = plan.price
        payment_history.checkout_session = stripe_response['subscription']['id']
        payment_history.save()
        return render(request,self.template_name)

class CancelledView(TemplateView):
    template_name = 'payment/payment_cancelled.html'

def cancel_checkout_session(request):
    if request.method == 'GET':
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            checkout_session_id = request.GET.get('checkout_session_id')
            stripe.Subscription.delete(checkout_session_id)
            payment = PaymentHistory.objects.get(checkout_session=checkout_session_id)            
            payment.delete()
            return JsonResponse({'success':True})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        