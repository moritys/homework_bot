import logging
import os
import time

from dotenv import load_dotenv

import requests

import telegram

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """
    Функция проверяет доступность переменных окружения,
    которые необходимы для работы программы.
    """
    try:
        return (PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID)
    except Exception as error:
        logging.critical(f'Error with env tokens: {error}')


def send_message(bot, message):
    """
    Функция отправляет сообщение в Telegram чат.
    Принимает на вход два параметра:
    экземпляр класса Bot и строку с текстом сообщения.
    """
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Message send')
    except Exception as error:
        logging.error(f'Error with sending message: {error}')


def get_api_answer(timestamp):
    """Функция делает запрос к единственному эндпоинту API-сервиса."""
    payload = {'from_date': timestamp}

    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        return response
    except Exception as error:
        logging.error(f'Error with main API response: {error}')


def check_response(response):
    """Функция проверяет ответ API на соответствие документации."""
    try:
        return response.json().get('homeworks')[0]
    except Exception as error:
        logging.error(f'Error with JSON: {error}')


def parse_status(homework):
    """
    Функция извлекает из информации о конкретной домашней работе её статус.
    """
    try:
        homework_name = homework.get('homework_name')
        status = homework.get('status')
        if status not in HOMEWORK_VERDICTS:
            logging.error('Unknown status of homework')
        verdict = HOMEWORK_VERDICTS[status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except Exception as error:
        logging.error(f'Error with status parsing: {error}')


def main():
    """
    Главная функция:
        - делает запрос к API
        - проверяет ответ
        - если есть обновления — получает статус работы из обновления
        и отправляет сообщение в Telegram.
    Время паузы между запросами 10 минут.
    """
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        timestamp = (int(time.time()) - 7889229)  # последние 3 месяца
    while True:
        try:
            response = get_api_answer(timestamp)
            message = parse_status(check_response(response))
            send_message(bot, message)
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            message = f'Bot is definitely dead: {error}'


if __name__ == '__main__':
    main()
