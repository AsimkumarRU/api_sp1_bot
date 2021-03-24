import os
import time

import logging
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)


def parse_homework_status(homework):
    
    verdicts = {
        'rejected': 'К сожалению в работе нашлись ошибки.',
        'approved': 'Ревьюеру всё понравилось, можно приступать ' \
                  'к следующему уроку.'
    }

    try:
        homework_name = homework.get('homework_name')
        current_verdict = verdicts[homework.get('status')]
        if homework.get('status') == 'reviewing':
            return f'Работа "{homework_name}" взята в ревью.'
        return f'У вас проверили работу "{homework_name}"!\n{current_verdict}'
    except Exception:
        logging.error('Неверный ответ сервера')


def get_homework_statuses(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    data = current_timestamp or int(time.time())
    try:
        homework_statuses = requests.get(
            url,
            params={'from_date': data}, headers=headers)
        return homework_statuses.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        logging.exception(f'Обнаружена ошибка. Error: {e}')
    return {}


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    # проинициализировать бота здесь
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot_client=bot_client)
            current_timestamp = new_homework.get(
                'current_date', current_timestamp)  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            logging.exception(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
