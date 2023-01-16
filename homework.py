...

load_dotenv()


PRACTICUM_TOKEN = 'y0_AgAAAAAZ_U-dAAYckQAAAADZqNQeA0J6aLIDTr-mZ7bZ2BdTGk-jZQI'
TELEGRAM_TOKEN = '5972478365:AAHwWtYsNRN0wYin4ipEfIG76gEum7PjpUE'
TELEGRAM_CHAT_ID = '310600320'

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
    Функция check_tokens() проверяет доступность переменных окружения,
    которые необходимы для работы программы. Если отсутствует хотя бы одна
    переменная окружения — продолжать работу бота нет смысла.
    """
    ...


def send_message(bot, message):
    """
    Функция send_message() отправляет сообщение в Telegram чат, определяемый
    переменной окружения TELEGRAM_CHAT_ID. Принимает на вход два параметра:
    экземпляр класса Bot и строку с текстом сообщения.
    """
    ...


def get_api_answer(timestamp):
    """
    Функция get_api_answer() делает запрос к единственному эндпоинту
    API-сервиса. В качестве параметра в функцию передается временная метка.
    В случае успешного запроса должна вернуть ответ API, приведя его
    из формата JSON к типам данных Python.
    """
    ...


def check_response(response):
    """
    Функция check_response() проверяет ответ API на соответствие документации.
    В качестве параметра функция получает ответ API, приведенный к типам данных
    Python.
    """
    ...


def parse_status(homework):
    """
    Функция parse_status() извлекает из информации о конкретной домашней работе
    статус этой работы. В качестве параметра функция получает только
    один элемент из списка домашних работ. В случае успеха, функция возвращает
    подготовленную для отправки в Telegram строку, содержащую один из вердиктов
    словаря HOMEWORK_VERDICTS.
    """
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """
    Функция main(): в ней описана основная логика работы программы.
    Все остальные функции должны запускаться из неё.
    Последовательность действий в общем виде должна быть примерно такой:
    Сделать запрос к API.
    Проверить ответ.
    Если есть обновления — получить статус работы из обновления и отправить
    сообщение в Telegram.
    Подождать некоторое время и вернуться в пункт 1.
    """

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    ...

    while True:
        try:

            ...

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
        ...


if __name__ == '__main__':
    main()
