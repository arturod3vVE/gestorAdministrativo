import requests
from bs4 import BeautifulSoup
from .models import ConfigSistema, HistorialTasa
from django.utils import timezone
import traceback
from decimal import Decimal, InvalidOperation
import urllib3

# Desactivar advertencias de SSL del BCV (suelen tener certificados vencidos)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_tasa_bcv():
    try:
        url = "https://www.bcv.org.ve/"
        # User-Agent para evitar que el servidor nos rechace por parecer un bot básico
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, verify=False, timeout=10, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            dolar_div = soup.find('div', {'id': 'dolar'})
            
            if dolar_div:
                tasa_text = dolar_div.find('strong').text.strip()
                # Convertimos directamente a Decimal
                # Ej: "36,12" -> "36.12" -> Decimal("36.12")
                try:
                    tasa_limpia = Decimal(tasa_text.replace(',', '.'))
                    return tasa_limpia
                except (InvalidOperation, ValueError):
                    print(f"Error de formato en la tasa: {tasa_text}")
                    return None
                
    except Exception as e:
        print(f"Error obteniendo BCV: {e}")
        return None
    
    return None

def actualizar_tasa_bcv_automatica():
    print("\n--- [DEBUG BCV] Iniciando proceso ---")
    url = "https://www.bcv.org.ve/"
    
    try:
        # User-Agent para evitar bloqueos básicos
        headers = {'User-Agent': 'Mozilla/5.0'} 
        response = requests.get(url, verify=False, timeout=15, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            dolar_div = soup.find('div', {'id': 'dolar'})
            
            if dolar_div:
                tasa_text = dolar_div.find('strong').text.strip()
                tasa_float = Decimal(tasa_text.replace(',', '.'))
                
                config, _ = ConfigSistema.objects.get_or_create(id=1)
                
                config.tasa_bcv = tasa_float
                config.save() 
                
                hoy = timezone.now().date()
                HistorialTasa.objects.update_or_create(
                    fecha=hoy,
                    defaults={'valor': tasa_float}
                )
                
                print(f"--- [DEBUG BCV] Éxito: Tasa {tasa_float} procesada.")
                return True
    except Exception as e:
        print(f"--- [DEBUG BCV] CRASH: {str(e)}")
    
    return False