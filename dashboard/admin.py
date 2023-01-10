from django.contrib import admin
from .models import TwitterAction,Campaign,CreativeFile,CampaignAction,DigitalGift,Plan,PaymentHistory


admin.site.register(TwitterAction)
admin.site.register(Campaign)
admin.site.register(CreativeFile)
admin.site.register(CampaignAction)
admin.site.register(DigitalGift)
admin.site.register(Plan)
admin.site.register(PaymentHistory)