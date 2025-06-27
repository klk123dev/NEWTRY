import requests
from bs4 import BeautifulSoup
import time
from telegram import Bot

# CONFIGURA AQUÍ (¡CAMBIALO!)
TOKEN = "7673003979:AAEGirwgoo9bn25jUz2QvfdubxZXOXaZNp8"  # Ej: "123456:ABC-DEF..."
CHAT_ID = "5397929116"  # Ej: "123456789"
EVENTOS = [
    "https://ra.co/events/2015270",  # Ejemplo (cámbialo)
    # Añade más eventos aquí: "https://ra.co/events/XXXXXX",
]

# --- NO TOCAR LO DE ABAJO ---
bot = Bot(token=TOKEN)
ultimo_estado = {}

def revisar_eventos():
    for url in EVENTOS:
        try:
            pagina = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            sopa = BeautifulSoup(pagina.text, 'html.parser')
            
            nombre = sopa.find("h1").text.strip() if sopa.find("h1") else "Evento RA"
            estado = "SOLD OUT" if sopa.find("span", class_="event-status") and "sold out" in sopa.find("span", class_="event-status").text.lower() else "DISPONIBLE"
            
            if url in ultimo_estado:
                if ultimo_estado[url] == "SOLD OUT" and estado == "DISPONIBLE":
                    bot.send_message(chat_id=CHAT_ID, text=f"🎟️ ¡ENTRADAS! 🎟️\n{nombre}\n{url}")
                    print("¡AVISO ENVIADO!")
            
            ultimo_estado[url] = estado
        except Exception as e:
            print(f"Error con {url}: {e}")

print("⚡ BOT ACTIVO. Monitoreando RA...")
while True:
    revisar_eventos()
    time.sleep(3)  # Revisa cada 3 segundos