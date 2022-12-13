from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404,reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from .decorators import twitter_login_required
from django.contrib.auth.decorators import user_passes_test
from .models import TwitterAuthToken, TwitterUser
from .authorization import create_update_user_from_twitter, check_token_still_valid
from twitter_api.twitter_api import TwitterAPI
from django.views.generic import ListView, DetailView, View, TemplateView, CreateView
from django.views.generic.edit import UpdateView
from accounts.models import User,Profile
from django.contrib.auth import views as auth_views
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm,SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserCreateForm, ProfiledAuthenticationForm, UserUpdateForm
from urllib.parse import urlencode
# Create your views here.
class LoginView(View):
    template_name = "registration/login.html"
    form_class = ProfiledAuthenticationForm
    
    def get_success_url(self):
        return reverse('authorization:index')
    
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
    
    return redirect(reverse("accounts:profile"))

@login_required
def change_email(request):
    new_email = request.POST.get('new_email')    
    try:
        user = User.objects.get(email=new_email)
        messages.add_message(request, messages.ERROR, '同じメールを持つユーザーが既に存在します。')
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

