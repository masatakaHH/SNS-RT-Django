from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.template import loader
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import (
    AuthenticationForm,PasswordResetForm,UsernameField
)
from accounts.models import User
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
import pytz

class UserCreateForm(UserCreationForm):
    username = forms.CharField(label="名前",required=True)
    email = forms.EmailField(label="メールアドレス", required=True)
    password1 = forms.CharField(label='パスワード', required=True, strip=False, widget=forms.PasswordInput())
    password2 = forms.CharField(label='パスワード確認', required=True, strip=False, widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ("username","email", "password1", "password2")

    def clean(self):
        super(UserCreateForm, self).clean()
        try:
            user = User.objects.get(email=self.cleaned_data['email'])
            raise forms.ValidationError("既にこのメールは存在する為、登録できません。")
        except User.DoesNotExist:
            pass
        
        try:
            user = User.objects.get(username=self.cleaned_data['username'])
            raise forms.ValidationError("既にこのユーザー名は存在する為、登録できません。")
        except User.DoesNotExist:
            pass

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        now = datetime.today().astimezone(pytz.timezone('Asia/Tokyo'))
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["username"]        
        user.is_active = True
        user.account_type = 2
        user.last_login=now
        user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="メールアドレス", required=True)    
    is_superuser = forms.IntegerField(label='ロール', required=True)
    
    class Meta:
        model = User
        fields = ("email", "is_superuser")

    def save(self, commit=True):
        user = super(UserUpdateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]        
        user.is_superuser = self.cleaned_data["is_superuser"]
        if commit:
            user.save()
        return user

class ProfiledAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label=_("メールアドレス"),
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True,'placeholder': 'メールアドレス'}),
    )
    password = forms.CharField(
        label=_("パスワード"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'パスワード'}),
    )
    #remember_me = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'scalero-checkbox','id':'remember-me'}))
    profile_error_messages = {
        "invalid_profile": _("メールアドレスまたはパスワードが正しくありません。"
        )
    }
    error_messages = {
        'invalid_login': _(
            "ログインできません。パスワードが分からない場合、管理者に連絡してください。"            
        ),
        
    }
    # def clean(self):
    #     super(ProfiledAuthenticationForm, self).clean()
    #     if self.user_cache:
    #         if not self.user_cache.twitteruser.can_login:
    #             raise forms.ValidationError(
    #                 self.profile_error_messages['invalid_profile'],
    #                 code='invalid_profile',
    #                 params={'username': self.username_field.verbose_name},
    #             )

class PasswordResetFormUpdate(PasswordResetForm):
    email = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True,'placeholder': 'メールアドレス'}),
    )
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        subject = "パスワード再設定"
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        
        #message = Mail(from_email=settings.EMAIL_FROM,to_emails=to_email,subject=subject,html_content=body)
        url = reverse_lazy('dashboard:password_reset_confirm',kwargs={'uidb64':context['uid'],'token':context['token']})        
        confirm_url = str(context['protocol'])+'://'+str(context['domain'])+str(url)
        html_body = render_to_string("registration/password_reset_email.html", {'url':confirm_url})
        
        message = Mail(
            from_email=settings.EMAIL_FROM,
            to_emails=to_email,
            subject=subject,
            html_content=html_body
        )
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
        except Exception as e:
            print(e)
    
class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)    