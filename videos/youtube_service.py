from googleapiclient.discovery import build
from django.conf import settings
from django.core.cache import cache
import hashlib
import logging

logger = logging.getLogger(__name__)

class YouTubeService2026:
    """Servicio YouTube Data API v3 - Optimizado 2026"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.YOUTUBE_API_KEY
        self.youtube = build(
            settings.YOUTUBE_API_SERVICE_NAME,
            settings.YOUTUBE_API_VERSION,
            developerKey=self.api_key
        )
    
    def buscar_videos_con_cache(self, query, max_results=10):
        """Busca videos con caché automático (2026 feature)"""
        
        # Generar clave de caché única
        cache_key = f"youtube_search_{hashlib.md5(query.encode()).hexdigest()}"
        
        # Intentar obtener de caché
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"✅ Cache HIT: {query}")
            return cached_result
        
        # Si no existe en caché, llamar a API
        logger.info(f"🔍 API CALL: {query}")
        
        search_response = self.youtube.search().list(
            q=query,
            part='id,snippet',
            type='video',
            maxResults=max_results,
            order='relevance',
            regionCode='MX'  # México
        ).execute()
        
        resultados = search_response.get('items', [])
        
        # Guardar en caché por 1 hora
        cache.set(cache_key, resultados, timeout=3600)
        
        return resultados
    
    def obtener_estadisticas_mejoradas(self, video_id):
        """Obtiene estadísticas con métricas 2026"""
        
        response = self.youtube.videos().list(
            part='snippet,contentDetails,statistics,topicDetails',
            id=video_id
        ).execute()
        
        if not response['items']:
            return None
        
        video = response['items'][0]
        stats = video.get('statistics', {})
        
        return {
            'views': int(stats.get('viewCount', 0)),
            'likes': int(stats.get('likeCount', 0)),
            'comments': int(stats.get('commentCount', 0)),
            'engagement_rate': self._calcular_engagement(stats),  # 🆕 2026
        }
    
    def _calcular_engagement(self, stats):
        """Calcula tasa de engagement (2026 metric)"""
        views = int(stats.get('viewCount', 0))
        if views == 0:
            return 0.0
        
        likes = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        
        engagement = ((likes + comments) / views) * 100
        return round(engagement, 2)