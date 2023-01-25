import logging
import logging.config
import os
import sys
import time
from http import HTTPStatus

from dotenv import load_dotenv

import exceptions as ex

import loggerconfig as log

import requests

import telegram


logging.config.dictConfig(log.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
THREE_MONTHS = 7889229
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """
    Функция проверяет доступность переменных окружения.
    При отсуствии хотя бы одного значения, прерывает работу программы.
    """
    logger.info('Начали проверку переменных окружения')
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляет статус домашки от бота пользователю."""
    logger.info('Пытаемся отправить сообщение')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Сообщение отправлено успешно: {message}')
    except Exception as error:
        logger.error(
            f'Сообщение не отправлено! Проверьте id чата: {TELEGRAM_CHAT_ID}. '
            f'Ошибка: {error}'
        )


def get_api_answer(timestamp):
    """Функция делает запрос к АПИ и возвращает ответ в формате json."""
    payload = {'from_date': timestamp}

    try:
        logger.info(f'Делаем запрос к эндпоинту: {ENDPOINT}')
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException as error:
        message = f'Код ответа API: {response.status_code}. Ошибка: {error}'
        raise requests.RequestException(message)
    if response.status_code != HTTPStatus.OK:
        raise ex.WrongAnswerStatus(
            f'Сервер вернул некорректный статус: {response.status_code}'
        )
    return response.json()


def check_response(response):
    """Функция проверяет корректность данных ответа сервера."""
    logger.info('Проверяем формат ответа сервера')
    if not isinstance(response, dict):
        raise TypeError('Сервер вернул не словарь')
    if response == []:
        logger.debug('В данных момент список домашек пуст')
    if len(response.get('homeworks')) == 0:
        logger.debug('В данный момент обновлений нет')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('Тип домашних работ не в виде списка')
    return response['homeworks']


def parse_status(homework):
    """Функция извлекает статус последней домашки из ответа сервера."""
    logger.info('Получаем статус последней домашки')
    homework_name = homework.get('homework_name')
    if not homework_name:
        raise ex.HaveNotHomeworkName(
            'В ответе API домашки нет ключа homework_name'
        )
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise ex.UnknownStatusException('Неизвестный статус домашки')
    verdict = HOMEWORK_VERDICTS[status]
    return (f'Изменился статус проверки работы "{homework_name}". {verdict}')


def main():
    """
    Невероятно, но факт.
    Это основная функция, запускающая все остальные
    с периодичностью в 10 минут.
    Первый запрос делается за последние три месяца.
    """
    if check_tokens() is False:
        logger.critical('Отсутствуют переменные окружения!')
        sys.exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = (int(time.time()) - THREE_MONTHS)
    message = ''
    old_message = ''
    homework = ()

    def logging_errors(message):
        logger.error(message)
        if old_message != message:
            send_message(bot, message)

    while True:
        logger.info('Запускаем главную функцию')
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if len(homework) > 0:
                message = parse_status(homework[0])
                send_message(bot, message)
            timestamp = response.get('current_date')
        except requests.RequestException as error:
            message = f'Проблема в работе API: {error}.'
            logging_errors(message)
        except ex.UnknownStatusException as error:
            message = f'Ошибка в обработке ответа: {error}.'
            logging_errors(message)
        except Exception as error:
            message = f'Что-то пошло не так: {error}'
            logging_errors(message)
        finally:
            old_message = message
            logger.info('Следующий запрос к серверу через 10 минут.')
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
