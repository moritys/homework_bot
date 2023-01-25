LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default_formatter': {
            'format': ('[%(levelname)s: %(asctime)s] %(message)s '
                       '| func: %(funcName)s, line: %(lineno)d |')
        },
    },

    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default_formatter',
            'stream': 'ext://sys.stdout',
        },
    },

    'loggers': {
        '__main__': {
            'handlers': ['stream_handler'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
