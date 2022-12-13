from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from .forms import ProfiledAuthenticationForm,PasswordResetFormUpdate
from . import views
app_name = 'accounts'

urlpatterns = [
    ## Login設定
    path('', views.UserDetailView.as_view(), name='profile-publish'),
    path('login/', auth_views.LoginView.as_view(form_class=ProfiledAuthenticationForm, redirect_authenticated_user=True), name="login"),
    path('logout', auth_views.LogoutView.as_view(), name='account_logout'),
    path('password-reset/',auth_views.PasswordResetView.as_view(form_class=PasswordResetFormUpdate,success_url=reverse_lazy('dashboard:password_reset_done')),name='password_reset'),
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('dashboard:password_reset_complete')),name='password_reset_confirm'),
    path('password-reset/complete/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path('signup/', views.Signup.as_view(), name='signup'),
    ## Twitter設定
    path('twitter_login/', views.twitter_login, name='twitter_login'),
    path('twitter_callback/', views.twitter_callback, name='twitter_callback'),
    path('twitter_logout/', views.twitter_logout, name='twitter_logout'),
    ## アカウント設定
    path('profile/', views.UserDetailView.as_view(), name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/email/', views.change_email, name='change_email'),
    path('profile/password/', views.change_password, name='change_password'),
    path('profile/update_user_photo', views.update_user_photo, name='update_user_photo'),
        
]