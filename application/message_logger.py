import logging
from logging.handlers import TimedRotatingFileHandler

from google.cloud.logging import Client

# google cloud logging client
client = Client()


class MessageLogger:
    """
    Message logger class that logs the data to the console
    """

    def __init__(self, module_name):
        """
        Class constructor - creates a message logger for the module
        :param module_name: the name of the module
        """
        self.__logger = logging.getLogger(module_name)
        self.__logger.setLevel(logging.DEBUG)
        #self.__console_handler = client.get_default_handler()
        self.__console_handler = TimedRotatingFileHandler("logs/app_logs.log", when="midnight") # for local logging
        self.__console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.__console_handler.setFormatter(formatter)
        self.__logger.addHandler(self.__console_handler)

    def get_logger(self):
        """
        Return the logger object that can be used for logging messages
        :return: logging object
        """
        return self.__logger

    def get_handler(self):
        """
        Return the handler object that can be used for logging messages
        :return: handler object
        """
        return self.__console_handler
