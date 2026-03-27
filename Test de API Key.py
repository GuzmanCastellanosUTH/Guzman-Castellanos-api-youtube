from googleapiclient.discovery import build

# Reemplaza con tu API Key
API_KEY = 'AIzaSyBlUh55TflOGcBY2euGSp_otNN8H3UPleY'

# Crear servicio YouTube
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Buscar videos de "Django tutorial"
request = youtube.search().list(
    q='Django tutorial',
    part='snippet',
    type='video',
    maxResults=5
)

response = request.execute()

# Mostrar resultados
for item in response['items']:
    print(f"✅ {item['snippet']['title']}")

print("\n🎉 ¡API Key funciona correctamente!")