import requests
import logging

logger = logging.getLogger(__name__)

YANDEX_API_KEY = '80842b69-5d43-45e4-bd58-51f372f4f673'  

def get_coordinates(address):
    try:
        url = f"https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": YANDEX_API_KEY,
            "geocode": address,
            "format": "json"
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        found = int(data['response']['GeoObjectCollection']['metaDataProperty']
                    ['GeocoderResponseMetaData']['found'])
        if found > 0:
            pos = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            lon, lat = pos.split()
            return [float(lat), float(lon)]
        else:
            logger.warning(f"Адрес не найден: {address}")
            return None
    except Exception as e:
        logger.error(f"Ошибка геокодирования: {e}")
        return None
