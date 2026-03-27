from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from functools import wraps
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from datetime import datetime
from .models import Video
import secrets

# ============ PERMITIR HTTP EN DESARROLLO ============
# ⚠️ SOLO PARA DESARROLLO LOCAL - NUNCA EN PRODUCCIÓN
if settings.DEBUG:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def require_youtube_auth(view_func):
    """Decorador que verifica autenticación con YouTube OAuth"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'youtube_credentials' not in request.session:
            messages.warning(request, 'Debes autorizar el acceso a YouTube primero.')
            return redirect('videos:oauth_authorize')
        return view_func(request, *args, **kwargs)
    return wrapper


def inicio(request):
    """Dashboard principal"""
    youtube_conectado = 'youtube_credentials' in request.session
    user_info = request.session.get('youtube_user_info', {})

    # Estadísticas básicas
    total_videos = 0
    vistas = 0
    likes = 0
    videos = []

    if youtube_conectado:
        try:
            creds_data = request.session.get('youtube_credentials')
            credentials = Credentials(**creds_data)
            youtube = build('youtube', 'v3', credentials=credentials)

            # Obtener videos del canal
            channels_response = youtube.channels().list(
                mine=True,
                part='statistics'
            ).execute()

            if channels_response.get('items'):
                stats = channels_response['items'][0]['statistics']
                total_videos = stats.get('videoCount', 0)
                vistas = stats.get('viewCount', 0)
        except:
            pass

    context = {
        'youtube_conectado': youtube_conectado,
        'user_info': user_info,
        'total_videos': total_videos,
        'vistas': vistas,
        'likes': likes,
        'videos': videos,
    }
    return render(request, 'videos/inicio.html', context)


def oauth_authorize(request):
    try:
        state = secrets.token_urlsafe(32)

        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=settings.YOUTUBE_SCOPES
        )

        # 🔥 FORZAR redirect_uri AQUÍ (NO en constructor)
        flow.redirect_uri = "https://ruizvegaluis.pythonanywhere.com/oauth/callback/"

        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            state=state
        )

        print("🚀 AUTH URL:", authorization_url)  # 👈 CLAVE

        request.session['oauth_state'] = state
        request.session.modified = True

        return redirect(authorization_url)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return redirect('videos:inicio')


def oauth_callback(request):
    """Callback de OAuth - Recibe el código de autorización"""
    try:
        # Debug: Ver qué hay en la sesión
        print(f"🔍 Sesión completa: {dict(request.session.items())}")

        # Obtener state de la URL
        state_from_url = request.GET.get('state')
        state_from_session = request.session.get('oauth_state')

        print(f"🔑 State desde URL: {state_from_url}")
        print(f"🔒 State desde sesión: {state_from_session}")

        # Verificación más flexible
        if not state_from_url:
            raise ValueError('No se recibió state en la URL')

        if not state_from_session:
            # Intentar recuperar de otra manera
            messages.warning(request, 'Sesión expirada. Reintentando autorización...')
            return redirect('videos:oauth_authorize')

        if state_from_url != state_from_session:
            raise ValueError(f'State mismatch: URL={state_from_url}, Session={state_from_session}')

        # Continuar con el flujo OAuth
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=settings.YOUTUBE_SCOPES,
            state=state_from_url,  # Usar el state de la URL
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        authorization_response = request.build_absolute_uri().replace('http://', 'https://')
        print(f"🌐 Authorization response URL: {authorization_response}")

        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials

        # Guardar credenciales en sesión
        request.session['youtube_credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

        # Obtener info del canal
        youtube = build('youtube', 'v3', credentials=credentials)
        channels_response = youtube.channels().list(
            mine=True,
            part='snippet,statistics'
        ).execute()

        if channels_response.get('items'):
            channel = channels_response['items'][0]
            request.session['youtube_user_info'] = {
                'channel_title': channel['snippet']['title'],
                'channel_id': channel['id'],
                'thumbnail': channel['snippet']['thumbnails']['default']['url'],
                'subscribers': channel['statistics'].get('subscriberCount', 'N/A')
            }

        # Limpiar state usado
        if 'oauth_state' in request.session:
            del request.session['oauth_state']

        request.session.modified = True

        messages.success(request, '✅ ¡Autenticación exitosa con YouTube!')
        return redirect('videos:inicio')

    except Exception as e:
        messages.error(request, f'❌ Error en callback OAuth: {str(e)}')
        import traceback
        print(traceback.format_exc())
        return redirect('videos:inicio')


@require_youtube_auth
def mis_videos(request):
    """Lista de videos del canal"""
    try:
        creds_data = request.session.get('youtube_credentials')
        credentials = Credentials(**creds_data)
        youtube = build('youtube', 'v3', credentials=credentials)

        # Obtener videos del canal
        request_videos = youtube.search().list(
            part='snippet',
            forMine=True,
            type='video',
            maxResults=50,
            order='date'
        )

        response = request_videos.execute()
        videos_list = []

        for item in response.get('items', []):
            video_id = item['id']['videoId']

            # Obtener estadísticas
            stats_response = youtube.videos().list(
                part='statistics',
                id=video_id
            ).execute()

            stats = stats_response['items'][0]['statistics'] if stats_response.get('items') else {}

            videos_list.append({
                'id': video_id,
                'youtube_id': video_id,
                'titulo': item['snippet']['title'],
                'url_thumbnail': item['snippet']['thumbnails']['medium']['url'],
                'canal_nombre': item['snippet']['channelTitle'],
                'fecha_publicacion': item['snippet']['publishedAt'],
                'vistas': stats.get('viewCount', 0),
                'likes': stats.get('likeCount', 0),
            })

        context = {
            'videos': videos_list,
            'total_views': sum(int(v.get('vistas', 0)) for v in videos_list),
            'total_likes': sum(int(v.get('likes', 0)) for v in videos_list),
            'total_comments': 0,
        }

        return render(request, 'videos/mis_videos.html', context)

    except Exception as e:
        messages.error(request, f'Error al cargar videos: {str(e)}')
        return redirect('videos:inicio')


@require_youtube_auth
def subir_video(request):
    """Formulario para subir video"""
    return render(request, 'videos/subir_video.html')


@require_youtube_auth
def procesar_subida(request):
    """Sube video a YouTube"""

    print(f"🎬 procesar_subida llamado - Método: {request.method}")

    if request.method == 'POST':
        try:
            print("📋 Datos del formulario:")
            print(f"   Archivos: {list(request.FILES.keys())}")
            print(f"   POST data: {list(request.POST.keys())}")

            # Verificar que el archivo existe
            if 'video' not in request.FILES:
                raise ValueError('No se recibió el archivo de video')

            video_file = request.FILES['video']

            # Obtener y limpiar datos del formulario
            titulo_raw = request.POST.get('titulo', '')
            descripcion_raw = request.POST.get('descripcion', '')

            print(f"📝 Datos RAW recibidos:")
            print(f"   Título RAW: '{titulo_raw}' (len={len(titulo_raw)})")
            print(f"   Descripción RAW: '{descripcion_raw[:50]}...' (len={len(descripcion_raw)})")

            # Limpiar y validar título
            titulo = titulo_raw.strip()

            # Si el título está vacío después de strip, usar nombre del archivo
            if not titulo:
                titulo = video_file.name.rsplit('.', 1)[0]  # Nombre sin extensión
                print(f"⚠️ Título vacío, usando nombre de archivo: {titulo}")

            # Limitar longitud del título (YouTube max: 100 caracteres)
            if len(titulo) > 100:
                titulo = titulo[:97] + '...'
                print(f"⚠️ Título recortado a 100 caracteres")

            # Limpiar descripción
            descripcion = descripcion_raw.strip()

            # Si está vacía, usar descripción por defecto
            if not descripcion:
                descripcion = f"Video subido desde Django - {titulo}"
                print(f"⚠️ Descripción vacía, usando por defecto")

            # Limitar longitud (YouTube max: 5000 caracteres)
            if len(descripcion) > 5000:
                descripcion = descripcion[:4997] + '...'

            categoria = request.POST.get('categoria', '27')
            privacidad = request.POST.get('privacidad', 'private')

            print(f"✅ Datos LIMPIOS:")
            print(f"   Título: '{titulo}' (len={len(titulo)})")
            print(f"   Descripción: '{descripcion[:50]}...' (len={len(descripcion)})")
            print(f"   Categoría: {categoria}")
            print(f"   Privacidad: {privacidad}")
            print(f"   Archivo: {video_file.name} ({video_file.size / (1024*1024):.2f} MB)")

            # Validaciones finales
            if not titulo or len(titulo.strip()) == 0:
                raise ValueError(f'El título no puede estar vacío. Recibido: "{titulo}"')

            if not descripcion or len(descripcion.strip()) == 0:
                raise ValueError(f'La descripción no puede estar vacía. Recibido: "{descripcion}"')

            # Obtener credenciales
            creds_data = request.session.get('youtube_credentials')
            if not creds_data:
                raise ValueError('No hay credenciales de YouTube en la sesión')

            print("🔑 Credenciales recuperadas")

            credentials = Credentials(**creds_data)
            youtube = build('youtube', 'v3', credentials=credentials)

            print("✅ Cliente de YouTube creado")

            # Guardar archivo temporalmente
            temp_path = os.path.join(settings.MEDIA_ROOT, video_file.name)
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            print(f"💾 Guardando en: {temp_path}")

            with open(temp_path, 'wb') as f:
                for chunk in video_file.chunks():
                    f.write(chunk)

            file_size_mb = os.path.getsize(temp_path) / (1024 * 1024)
            print(f"✅ Archivo guardado ({file_size_mb:.2f} MB)")

            # Metadata del video - ASEGURAR QUE NO HAYA VALORES VACÍOS
            body = {
                'snippet': {
                    'title': str(titulo),  # Convertir a string explícitamente
                    'description': str(descripcion),
                    'categoryId': str(categoria)
                },
                'status': {
                    'privacyStatus': str(privacidad)
                }
            }

            # Debug: Imprimir el body que se enviará a YouTube
            print("📤 Metadata que se enviará a YouTube:")
            import json
            print(json.dumps(body, indent=2, ensure_ascii=False))

            print("⬆️ Iniciando subida a YouTube...")

            media = MediaFileUpload(temp_path, resumable=True, chunksize=1024*1024)

            request_upload = youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )

            # Subir con progreso
            response = None
            while response is None:
                status, response = request_upload.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"⬆️ Progreso: {progress}%")

            print(f"✅ Video subido exitosamente!")
            print(f"   ID: {response['id']}")
            print(f"   Título: {response['snippet']['title']}")
            print(f"   URL: https://www.youtube.com/watch?v={response['id']}")

            # Eliminar archivo temporal
            try:
                os.remove(temp_path)
                print("🗑️ Archivo temporal eliminado")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar: {e}")

            messages.success(
                request,
                f'✅ Video "{response["snippet"]["title"]}" subido exitosamente! '
                f'<a href="https://www.youtube.com/watch?v={response["id"]}" target="_blank" class="alert-link">Ver en YouTube</a>'
            )

            return redirect('videos:mis_videos')

        except Exception as e:
            error_msg = str(e)
            print(f"❌ ERROR: {error_msg}")

            import traceback
            print("📋 Stack trace completo:")
            print(traceback.format_exc())

            messages.error(request, f'❌ Error al subir video: {error_msg}')
            return redirect('videos:subir_video')

    else:
        print("⚠️ Método no es POST")
        return redirect('videos:subir_video')


def detalle_video(request, video_id):
    """Detalle de un video"""
    try:
        youtube = build(
            settings.YOUTUBE_API_SERVICE_NAME,
            settings.YOUTUBE_API_VERSION,
            developerKey=settings.YOUTUBE_API_KEY
        )

        response = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        ).execute()

        if response.get('items'):
            item = response['items'][0]
            video = {
                'youtube_id': video_id,
                'titulo': item['snippet']['title'],
                'descripcion': item['snippet']['description'],
                'url_video': f'https://www.youtube.com/watch?v={video_id}',
                'url_thumbnail': item['snippet']['thumbnails']['high']['url'],
                'canal_nombre': item['snippet']['channelTitle'],
                'canal_id': item['snippet']['channelId'],
                'fecha_publicacion': item['snippet']['publishedAt'],
                'vistas': item['statistics'].get('viewCount', 0),
                'likes': item['statistics'].get('likeCount', 0),
                'comentarios': item['statistics'].get('commentCount', 0),
                'duracion': item['contentDetails']['duration'],
                'categoria': 'YouTube',
                'etiquetas': item['snippet'].get('tags', []),
            }

            # Añadir método get_embed_url
            video['embed_url'] = f"https://www.youtube.com/embed/{video_id}"

            context = {'video': type('obj', (object,), video)}
            return render(request, 'videos/detalle_video.html', context)

    except Exception as e:
        messages.error(request, f'Error al cargar video: {str(e)}')

    return redirect('videos:inicio')


def buscar_videos(request):
    """Buscar videos en YouTube"""
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
            messages.error(request, f'Error en búsqueda: {str(e)}')

    return render(request, 'videos/buscar.html', {
        'query': query,
        'resultados': resultados
    })