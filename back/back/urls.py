from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import CustomSignUpView

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include('movies.urls')),
    path('accounts/signup/', CustomSignUpView.as_view(), name='custom_signup'),
    path('accounts/', include('dj_rest_auth.urls')),
    path('silk/', include('silk.urls', namespace='silk')),
    path('api/chatbot/', include('reelbots.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
