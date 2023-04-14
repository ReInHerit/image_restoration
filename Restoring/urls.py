
from django.urls import include, path
from . import views
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
router = routers.DefaultRouter()
urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('landing', views.landing, name='landing'),
    # path('api-auth/', include('rest_framework.urls')),
    path('upload/image/', views.upload_image, name='upload_image'),
    path('delete/folder/', views.delete_temp_folder, name='delete_folder'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT[0])
