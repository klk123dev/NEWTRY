import requests
from bs4 import BeautifulSoup
import time
from telegram import Bot, error as telegram_error
import logging

# Configuración - ¡EDITA ESTO!
CONFIG = {
    "TELEGRAM_TOKEN": "7673003979:AAEGirwgoo9bn25jUz2QvfdubxZXOXaZNp8",          # Reemplaza con tu token
    "CHAT_ID": "5397929116",              # Reemplaza con tu chat ID
    "EVENTOS": [
        "https://ra.co/events/2015270",        # Evento de ejemplo
        # Añade más eventos aquí
    ],
    "INTERVALO": 3,                            # Segundos entre chequeos
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Configuración avanzada
HEADERS = {"User-Agent": CONFIG["USER_AGENT"]}
bot = Bot(token=CONFIG["TELEGRAM_TOKEN"])
estados_previos = {}

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def verificar_evento(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer información del evento
        nombre = soup.find("h1", {"class": "event-title"}).get_text(strip=True)
        estado_tag = soup.find("span", {"class": "event-status"})
        
        if estado_tag:
            estado_actual = "DISPONIBLE" if "sold out" not in estado_tag.text.lower() else "SOLD OUT"
        else:
            estado_actual = "DISPONIBLE"  # Si no encuentra el tag, asumimos que hay tickets
            
        return nombre, estado_actual
        
    except Exception as e:
        logger.error(f"Error al verificar {url}: {str(e)}")
        return None, None

def enviar_alerta(evento, url):
    mensaje = f"🎟️ ¡ENTRADAS DISPONIBLES! 🎟️\n\n{evento}\n\n{url}"
    try:
        bot.send_message(chat_id=CONFIG["CHAT_ID"], text=mensaje)
        logger.info(f"Alerta enviada: {evento}")
    except telegram_error.TelegramError as e:
        logger.error(f"Error al enviar mensaje: {str(e)}")

def monitorear():
    logger.info("Iniciando monitoreo de eventos...")
    while True:
        for url in CONFIG["EVENTOS"]:
            nombre, estado = verificar_evento(url)
            
            if nombre and estado:
                if url in estados_previos:
                    if estados_previos[url] == "SOLD OUT" and estado == "DISPONIBLE":
                        enviar_alerta(nombre, url)
                
                estados_previos[url] = estado
                
        time.sleep(CONFIG["INTERVALO"])

if __name__ == "__main__":
    # Validar configuración
    if not CONFIG["TELEGRAM_TOKEN"] or not CONFIG["CHAT_ID"]:
        logger.error("Falta configurar el token o chat ID de Telegram")
    elif not CONFIG["EVENTOS"]:
        logger.error("No hay eventos configurados para monitorear")
    else:
        monitorear()
