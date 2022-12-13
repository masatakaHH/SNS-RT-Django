from django import forms
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from accounts.models import User
from datetime import datetime
from django.contrib.auth.forms import (
    AuthenticationForm,PasswordResetForm,UsernameField
)
import pytz
       
class AddUserCreateForm(UserCreationForm):
    email = forms.EmailField(label="メールアドレス", required=True)
    last_name_jp = forms.CharField(label='名字', required=True)
    last_name_kana = forms.CharField(label='名字_カタカナ', required=True)
    first_name_jp = forms.CharField(label='名前', required=True)
    first_name_kana = forms.CharField(label='名前_カタカナ', required=True)    
    password1 = forms.CharField(label='パスワード', required=True, strip=False, widget=forms.PasswordInput())
    password2 = forms.CharField(label='パスワード確認', required=True, strip=False, widget=forms.PasswordInput())
    role = forms.IntegerField(label='ロール', required=True)
    
    class Meta:
        model = User
        fields = ("email", "last_name_jp", "last_name_kana","first_name_jp", "first_name_kana", "password1", "password2", "role")
        
    def clean(self):        
        try:
            user = User.objects.get(email=self.cleaned_data['email'])
            print("同じメールを持つユーザーが既に存在します。")
            raise forms.ValidationError("同じメールを持つユーザーが既に存在します。")
        except User.DoesNotExist:
            pass        
        
    def clean_password2(self):  
        password1 = self.cleaned_data['password1']  
        password2 = self.cleaned_data['password2']  
  
        if password1 and password2 and password1 != password2:  
            raise ValidationError("Password don't match")  
        return password2 
        
    def save(self, commit=True):
        user = User()
        user.email = self.cleaned_data["email"]
        user.last_name_jp = self.cleaned_data["last_name_jp"]
        user.last_name_kana = self.cleaned_data["last_name_kana"]
        user.first_name_jp = self.cleaned_data["first_name_jp"]
        user.first_name_kana = self.cleaned_data["first_name_kana"]
        user.password = make_password(self.cleaned_data["password1"])
        role = self.cleaned_data["role"]
        if role == 2:
            user.is_staff = 1
        elif role == 1:
            user.is_staff = 1
            user.is_superuser = 1
        else:
            user.is_superuser = 0
            
        user.is_active = True
        user.save()
        allauth_emailconfirmation = EmailAddress(user=user, email=self.cleaned_data["email"], verified=True, primary=True)
        allauth_emailconfirmation.save()
        
        return user
    
    def get_role(self,obj):
        if obj.is_superuser:
            return '管理者'
        if obj.is_staff:
            return '編集者'
        else:
            return '一般'
        
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="メールアドレス", required=True)
    last_name_jp = forms.CharField(label='名字', required=True)
    last_name_kana = forms.CharField(label='名字_カタカナ', required=True)
    first_name_jp = forms.CharField(label='名前', required=True)
    first_name_kana = forms.CharField(label='名前_カタカナ', required=True)
    class Meta:
        model = User
        fields = ("email", "last_name_jp", "last_name_kana", "first_name_jp","first_name_kana")

    def save(self, commit=True):
        user = super(UserUpdateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.last_name_jp = self.cleaned_data["last_name_jp"]
        user.last_name_kana = self.cleaned_data["last_name_kana"]
        user.first_name_jp = self.cleaned_data["first_name_jp"]
        user.first_name_kana = self.cleaned_data["first_name_kana"]      
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
    
    def clean(self):
        super(ProfiledAuthenticationForm, self).clean()
               