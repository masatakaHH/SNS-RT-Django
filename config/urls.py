from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.conf import settings
from decorator_include import decorator_include
from django.contrib.auth.decorators import login_required

from django.conf.urls import (handler400, handler403, handler404, handler500)

handler404 = 'core.views.custom_page_not_found_view'
handler500 = 'core.views.custom_error_view'
handler403 = 'core.views.custom_permission_denied_view'
handler400 = 'core.views.custom_bad_request_view'

urlpatterns = [    
    path('accounts/', include(('accounts.urls', 'accounts'),namespace='accounts')),
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    
]

if not settings.PRODUCTION:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)