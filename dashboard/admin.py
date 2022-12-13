from django.contrib import admin
from .models import TwitterAction,Campaign,CreativeFile,CampaignAction,DigitalGift


admin.site.register(TwitterAction)
admin.site.register(Campaign)
admin.site.register(CreativeFile)
admin.site.register(CampaignAction)
admin.site.register(DigitalGift)