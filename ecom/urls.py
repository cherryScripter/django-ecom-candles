from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('store.urls')),
                  path('cart/', include('cart.urls')),
                  path('payment/', include('payment.urls')),

              ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Serve media files in production (DEBUG=False)
# if not settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# else:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
