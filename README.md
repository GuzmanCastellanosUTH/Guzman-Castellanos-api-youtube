# 🎥 YouTube Video Manager - Django + YouTube Data API v3

## 📋 Descripción del Proyecto
Sistema de gestión de videos de YouTube integrado con Django que permite:
- Listar videos del canal automáticamente
- Subir videos directamente desde Django
- Ver estadísticas (vistas, likes, comentarios)
- Gestionar playlist
- Obtener metadatos de videos
- Panel de administración completo

## 👨‍🎓 Información del Alumno
- **Nombre Completo:** [TU NOMBRE]
- **Matrícula:** [TU MATRÍCULA]
- **Carrera:** [TU CARRERA]
- **Semestre:** [TU SEMESTRE]
- **Materia:** Servicios Web RESTful
- **Profesor:** [NOMBRE DEL PROFESOR]
- **Ciclo:** 2026-1

## 🚀 Tecnologías Utilizadas
- Python 3.x
- Django 4.2.x
- YouTube Data API v3
- Google OAuth 2.0
- google-api-python-client
- google-auth-oauthlib
- MySQL
- Bootstrap 5.3.0

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone [URL_DE_TU_REPO]
cd youtube_project
```

### 2. Crear entorno virtual
```bash
python -m venv venv
.\venv\Scripts\Activate  # Windows
source venv/bin/activate # Linux/Mac
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Google Cloud Console
1. Ve a https://console.cloud.google.com/
2. Crea un nuevo proyecto
3. Habilita "YouTube Data API v3"
4. Crea credenciales OAuth 2.0
5. Descarga client_secrets.json
6. Coloca el archivo en la raíz del proyecto

### 5. Configurar URIs de redirección
```
http://localhost:8000/oauth2callback
http://127.0.0.1:8000/oauth2callback
```

### 6. Aplicar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crear superusuario
```bash
python manage.py createsuperuser
```

### 8. Ejecutar servidor
```bash
python manage.py runserver
```

### 9. Autenticarse con YouTube
- Visita http://127.0.0.1:8000/
- Clic en "Conectar con YouTube"
- Autoriza la aplicación con tu cuenta de Google
- Se generará token.pickle automáticamente

## 📸 Capturas de Pantalla
(Ver carpeta `screenshots/`)
1. Dashboard principal con videos
2. Formulario subir video
3. Lista de mis videos
4. Vista detallada con estadísticas
5. Google Cloud Console - API habilitada
6. OAuth consent screen

## 🧪 Pruebas Realizadas
- ✅ Autenticación OAuth 2.0 funcional
- ✅ Listar videos del canal
- ✅ Subir video a YouTube
- ✅ Obtener estadísticas en tiempo real
- ✅ Templates renderizando correctamente
- ✅ Refresh token automático

## 🔐 Seguridad
- ⚠️ `client_secrets.json` está en `.gitignore`
- ⚠️ `token.pickle` está en `.gitignore`
- ⚠️ Credenciales NO incluidas en el código
- ⚠️ OAuth 2.0 con scopes mínimos necesarios

## 📝 Notas Adicionales
- Cuota diaria: 10,000 unidades
- Subir video cuesta 1,600 unidades
- Verificar disponibilidad de cuota en Cloud Console

## 📚 Referencias
- YouTube Data API: https://developers.google.com/youtube/v3
- Google Cloud Console: https://console.cloud.google.com/
- Django Docs: https://docs.djangoproject.com/

## 📄 Licencia
Este proyecto es para fines educativos - UTH 2026-1
