from django.urls import path
from dashboard.views import dashboard_views, home_views,notification_views

app_name = 'dashboard'

urlpatterns = [
    ## ユーザー管理
    path('', home_views.HomeView.as_view(), name='toppage'),
    path('<str:campaign_id>', home_views.CampaignView.as_view(), name='campaign-publish'),
    path('home', home_views.HomeView.as_view(), name='homeview'),    
    path('dashboard/', dashboard_views.DashnoardView.as_view(), name='dashboardview'),
    path('dashboard/campaign/<str:pk>', dashboard_views.CampaignDetail.as_view(), name='campaign-detail'),
    path('dashboard/campaign-create/', dashboard_views.CampaignCreate.as_view(), name='campaign-create'), 
    path('dashboard/campaign-edit/<str:campaign_id>', dashboard_views.CampaignUpdate.as_view(), name='campaign-edit'),
    path('dashboard/campaign-edit/update/', dashboard_views.campaign_update, name='campaign-update'),
    
]
