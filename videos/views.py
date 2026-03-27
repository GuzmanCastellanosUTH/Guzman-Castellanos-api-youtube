from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings

# Google API Client
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import os
import json
from datetime import datetime

from .models import Video

# ⚠️ IMPORTANTE: Permitir HTTP para desarrollo local
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# ============================================================
# VISTAS DE AUTENTICACIÓN
# ============================================================

def login_view(request):
    """Vista de login de usuarios"""
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            
            # Redirigir a la página solicitada o al inicio
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'videos/login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('videos:inicio')
    return redirect('videos:inicio')


def registro_view(request):
    """Registro de nuevos usuarios"""
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Validaciones
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'videos/registro.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return render(request, 'videos/registro.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado')
            return render(request, 'videos/registro.html')
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Login automático
        login(request, user)
        messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido {username}')
        return redirect('videos:inicio')
    
    return render(request, 'videos/registro.html')


# ============================================================
# VISTAS PRINCIPALES
# ============================================================

def inicio(request):
    """Dashboard principal con videos destacados"""
    
    videos = Video.objects.all().order_by('-fecha_publicacion')[:12]
    
    contexto = {
        'videos': videos,
        'total_videos': Video.objects.count(),
        'total_views': sum(v.vistas for v in videos) if videos else 0,
        'total_likes': sum(v.likes for v in videos) if videos else 0,
    }
    
    return render(request, 'videos/inicio.html', contexto)


# ============================================================
# OAUTH YOUTUBE
# ============================================================

@login_required
def oauth_authorize(request):
    """Redirige a Google OAuth para autorización"""
    
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    
    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=settings.YOUTUBE_SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )
        
        # flow.authorization_url genera automáticamente el code_verifier internamente
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # 🔥 CLAVE: Guardamos el state Y el code_verifier en la sesión
        request.session['oauth_state'] = state
        request.session['oauth_verifier'] = flow.code_verifier 
        
        request.session.modified = True
        print(f"DEBUG: State guardado: {state}")
        
        return redirect(authorization_url)
        
    except Exception as e:
        messages.error(request, f'❌ Error al iniciar OAuth: {str(e)}')
        return redirect('videos:inicio')


def oauth_callback(request):
    """Recibe código de autorización y obtiene tokens"""
    
    # 1. Recuperar datos de la sesión
    state_session = request.session.get('oauth_state')
    verifier = request.session.get('oauth_verifier')
    
    state_url = request.GET.get('state')
    
    print(f"DEBUG: Verifier recuperado: {'SÍ' if verifier else 'NO'}")
    
    if not state_session or state_session != state_url:
        messages.error(request, '❌ Error de validación de estado (State mismatch).')
        return redirect('videos:oauth_authorize')
    
    try:
        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }
        
        # 2. Re-instanciar el flow con el state de la URL
        flow = Flow.from_client_config(
            client_config,
            scopes=settings.YOUTUBE_SCOPES,
            state=state_url,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )
        
        # 3. 🔥 ASIGNAR EL VERIFICADOR ANTES DE PEDIR EL TOKEN
        flow.code_verifier = verifier

        # 4. Obtener el token
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)
        
        credentials = flow.credentials
        
        # 5. Guardar credenciales
        request.session['youtube_credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Limpiar sesión
        if 'oauth_state' in request.session: del request.session['oauth_state']
        if 'oauth_verifier' in request.session: del request.session['oauth_verifier']
        
        messages.success(request, '✅ Conectado exitosamente con YouTube')
        return redirect('videos:subir_video')
        
    except Exception as e:
        print(f"Error detallado en callback: {str(e)}")
        messages.error(request, f'❌ Error en callback: {str(e)}')
        return redirect('videos:oauth_authorize')


# ============================================================
# BÚSQUEDA DE VIDEOS
# ============================================================

def buscar_videos(request):
    """Busca videos en YouTube por palabra clave"""
    
    query = request.GET.get('q', '')
    resultados = []
    
    if query:
        try:
            youtube = build(
                settings.YOUTUBE_API_SERVICE_NAME,
                settings.YOUTUBE_API_VERSION,
                developerKey=settings.YOUTUBE_API_KEY
            )
            
            search_response = youtube.search().list(
                q=query,
                part='id,snippet',
                type='video',
                maxResults=20
            ).execute()
            
            resultados = search_response.get('items', [])
        except Exception as e:
            messages.error(request, f'❌ Error en búsqueda: {str(e)}')
    
    return render(request, 'videos/buscar.html', {
        'query': query,
        'resultados': resultados
    })


# ============================================================
# SUBIR VIDEOS
# ============================================================

@login_required
def subir_video(request):
    """Muestra formulario para subir video"""
    
    # Verificar si ya está autenticado
    tiene_credenciales = 'youtube_credentials' in request.session
    
    return render(request, 'videos/subir_video.html', {
        'tiene_credenciales': tiene_credenciales
    })


@login_required
def procesar_subida(request):
    """Sube video a YouTube usando OAuth del usuario"""
    
    if request.method != 'POST':
        messages.error(request, '❌ Método no permitido')
        return redirect('videos:subir_video')
    
    # Verificar credenciales
    creds_data = request.session.get('youtube_credentials')
    if not creds_data:
        messages.error(request, '❌ No estás autorizado. Conecta con YouTube primero.')
        return redirect('videos:oauth_authorize')
    
    try:
        # Reconstruir credenciales
        credentials = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data.get('refresh_token'),
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=creds_data.get('scopes')
        )
        
        # Crear servicio YouTube
        youtube = build('youtube', 'v3', credentials=credentials)
        
        # Obtener datos del formulario
        if 'video' not in request.FILES:
            messages.error(request, '❌ No se seleccionó ningún archivo de video')
            return redirect('videos:subir_video')
        
        video_file = request.FILES['video']
        titulo = request.POST.get('titulo', 'Sin título')
        descripcion = request.POST.get('descripcion', '')
        categoria = request.POST.get('categoria', '27')
        privacidad = request.POST.get('privacidad', 'private')
        
        # Validar tamaño del archivo
        max_size = 2 * 1024 * 1024 * 1024  # 2GB
        if video_file.size > max_size:
            messages.error(request, '❌ El archivo es demasiado grande (máximo 2GB)')
            return redirect('videos:subir_video')
        
        # Crear directorio temporal
        temp_dir = '/tmp/youtube_uploads'
        os.makedirs(temp_dir, exist_ok=True)
        
        # Guardar archivo temporalmente
        temp_path = os.path.join(temp_dir, video_file.name)
        with open(temp_path, 'wb') as f:
            for chunk in video_file.chunks():
                f.write(chunk)
        
        # Metadata del video
        body = {
            'snippet': {
                'title': titulo,
                'description': descripcion,
                'categoryId': categoria,
                'tags': ['educación', 'tutorial']
            },
            'status': {
                'privacyStatus': privacidad,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Preparar archivo para upload
        media = MediaFileUpload(
            temp_path,
            chunksize=1024*1024,
            resumable=True
        )
        
        # Ejecutar upload
        request_upload = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        # Upload con progreso
        response = None
        while response is None:
            status, response = request_upload.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"Subido {progress}%")
        
        # Limpiar archivo temporal
        try:
            os.remove(temp_path)
        except:
            pass
        
        # Guardar en base de datos
        Video.objects.create(
            youtube_id=response['id'],
            titulo=titulo,
            descripcion=descripcion,
            url_video=f"https://www.youtube.com/watch?v={response['id']}",
            url_thumbnail=f"https://img.youtube.com/vi/{response['id']}/maxresdefault.jpg",
            canal_id=response['snippet']['channelId'],
            canal_nombre=response['snippet']['channelTitle'],
            fecha_publicacion=datetime.now(),
            categoria='otro',
            agregado_por=request.user
        )
        
        messages.success(
            request, 
            f'✅ Video subido exitosamente! ID: {response["id"]}'
        )
        return redirect('videos:mis_videos')
        
    except Exception as e:
        messages.error(request, f'❌ Error al subir video: {str(e)}')
        print(f"Error detallado: {e}")
        
        # Limpiar archivo temporal
        try:
            if 'temp_path' in locals():
                os.remove(temp_path)
        except:
            pass
        
        return redirect('videos:subir_video')


# ============================================================
# GESTIÓN DE VIDEOS
# ============================================================

def detalle_video(request, video_id):
    """Muestra detalles de un video"""
    video = get_object_or_404(Video, youtube_id=video_id)
    return render(request, 'videos/detalle_video.html', {
        'video': video
    })


@login_required
def mis_videos(request):
    """Muestra videos subidos por el usuario"""
    videos = Video.objects.filter(agregado_por=request.user).order_by('-creado')
    return render(request, 'videos/mis_videos.html', {
        'videos': videos
    })