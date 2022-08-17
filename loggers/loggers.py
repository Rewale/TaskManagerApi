from loguru import logger

# логгер отправки повторных сообщений
logger.add('logs/notification.log',
           format="[{time} {level} {message}",
           filter=lambda record: "notification_logger" in record["extra"],
           rotation="1 MB",
           compression="tar.gz")

notification_logger = logger.bind(notification_logger=True)
