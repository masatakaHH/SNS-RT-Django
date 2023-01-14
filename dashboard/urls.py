from django.urls import path
from dashboard.views import dashboard_views, home_views,notification_views

app_name = 'dashboard'

urlpatterns = [
    ## マイキャンペーン
    path('', home_views.TopPageView.as_view(), name='toppage'),
    path('campaign/<str:campaign_id>/', dashboard_views.ApplicantPush.as_view(), name='campaign-publish'),
    path('home/', home_views.HomeView.as_view(), name='homeview'),    
    path('dashboard/', dashboard_views.DashnoardView.as_view(), name='dashboardview'),
    path('dashboard/campaign/<str:pk>', dashboard_views.CampaignDetail.as_view(), name='campaign-detail'),
    path('dashboard/campaign/<str:pk>/delete/', dashboard_views.campaign_delete, name='campaign-delete'),
    path('dashboard/campaign-create/', dashboard_views.CampaignCreate.as_view(), name='campaign-create'), 
    path('dashboard/campaign/<str:campaign_id>/edit', dashboard_views.CampaignUpdate.as_view(), name='campaign-edit'),    
    path('dashboard/campaign-gift/update/', dashboard_views.gift_update, name='gift-update'),
    
    path('legal/', home_views.LegalView.as_view(), name='legal'),
    path('about/', home_views.AboutView.as_view(), name='about'),
    path('tos/', home_views.TermofServiceView.as_view(), name='tos'),
    
    path('applicant/', dashboard_views.ApplicantPush.as_view(), name='applicant'),
]
