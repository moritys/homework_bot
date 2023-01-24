import logging
import os
import sys
import time

from dotenv import load_dotenv

import exceptions as ex

import requests

import telegram


logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s',
)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


load_dotenv()


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
    Функция проверяет доступность переменных окружения.
    При отсуствии хотя бы одного значения, прерывает работу программы.
    """
    logger.info('Начали проверку переменных окружения')
    if not (PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID):
        logger.critical('Отсутствуют переменные окружения!')
        raise ex.HaveNotEnvException('Отсутствуют переменные окружения!')


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
    except requests.exceptions.HTTPError as error:
        message = f'Недоступен эндпоинт: {error}'
        logger.error(message)
        raise requests.exceptions.HTTPError(message)
    except requests.exceptions.Timeout as error:
        message = f'Недоступен эндпоинт: {error}'
        logger.error(message)
        raise requests.exceptions.Timeout(message)
    except requests.exceptions.InvalidURL as error:
        message = f'Проблема с URL: {error}. Текущее значение URL: {ENDPOINT}'
        logger.error(message)
        raise requests.exceptions.InvalidURL(message)
    except requests.RequestException as error:
        message = f'Код ответа API: {response.status_code}. Ошибка: {error}'
        logger.error(message)
        raise requests.RequestException(message)
    else:
        logger.info('✅Эндпоинт доступен и вернул ответ')
    if response.status_code != 200:
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
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('Тип домашних работ не в виде списка')
    if response.get('homeworks') == ():
        raise ex.HomeworkListIsEmpty('В ответе апи нет ключа homeworks')
    return response.get('homeworks')[0]


def parse_status(homework):
    """Функция извлекает статус последней домашки из ответа сервера."""
    logger.info('Получаем статус последней домашки')
    homework_name = homework.get('homework_name')
    if not homework_name:
        raise ex.HaveNotHomeworkName(
            'В ответе API домашки нет ключа homework_name'
        )
    status = homework.get('status')
    if status in HOMEWORK_VERDICTS:
        verdict = HOMEWORK_VERDICTS[status]
        return (
            f'Изменился статус проверки работы "{homework_name}". '
            f'{verdict}'
        )
    else:
        raise ex.UnknownStatusException('Неизвестный статус домашки')


def main():
    """
    Основная функция, запускающая все остальные:
    - проверяет токены
    - делает запрос к апи
    - проверяет ответ
    - отправляет сообщение, если есть обновления
    - оправшивает апи раз в 10 минут, пока запущена.
    """
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = (int(time.time()) - 7889229)  # последние 3 месяца

    while True:
        try:
            logger.info('Запускаем главную функцию')
            response = get_api_answer(timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            send_message(bot, message)
            timestamp = response.get('current_date')
        except Exception as error:
            message = f'Что-то пошло не так: {error}'
            logger.error(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
