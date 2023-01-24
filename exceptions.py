class HaveNotEnvException(Exception):
    """Отсутствуют переменные окружения."""

    pass


class NotSendMessagesException(Exception):
    """Сообщение не отправлено."""

    pass


class UnknownStatusException(Exception):
    """Получен неизвестный статус домашки."""

    pass


class WrongAnswerStatus(Exception):
    """Апи вернул не 200 ответом сервера."""

    pass


class HaveNotHomeworkName(Exception):
    """Апи не вернул имя домашки."""

    pass


class HomeworkListIsEmpty(Exception):
    """Апи вернул пустой список."""

    pass
