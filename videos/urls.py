from django.urls import path
from . import views
from . import youtube_service

app_name = 'videos'

urlpatterns = [
    # Página principal (NO requiere autenticación)
    path('', views.inicio, name='inicio'),
    
    # OAuth 2.0 (NO requiere autenticación de Django)
    path('oauth/authorize/', views.oauth_authorize, name='oauth_authorize'),
    path('oauth/callback/', views.oauth_callback, name='oauth_callback'),
    #path('oauth/logout/', views.oauth_logout, name='oauth_logout'),
    
    # Funcionalidades públicas
    path('buscar/', views.buscar_videos, name='buscar_videos'),
    path('video/<str:video_id>/', views.detalle_video, name='detalle_video'),
    
    # Funcionalidades que requieren OAuth
    path('mis-videos/', views.mis_videos, name='mis_videos'),
    path('subir/', views.subir_video, name='subir_video'),
    path('subir/procesar/', views.procesar_subida, name='procesar_subida'),
]