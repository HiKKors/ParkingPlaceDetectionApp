from kafka import KafkaProducer
import json
from logger import auth_logger

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer = lambda v:json.dumps(v).encode('utf-8')
)

def send_registration_event(user_data):
    topic = 'user_registrations'
    
    try:
        producer.send(topic, user_data)
        producer.flush()
        auth_logger.info('Отправлены данные о регистрации пользователя %s', user_data.get('username'))
    except Exception as e:
        auth_logger.error('Ошибка при отправке данных о регистрации: %s', str(e))