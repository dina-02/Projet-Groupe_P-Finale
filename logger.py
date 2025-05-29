import logging

class Logger:
    def __init__(self, config: dict):
        """
        Initialize logger configuration.
        """
        self.config = config

    def set_log(self) -> None:
        """
        Set the logger.
        :return: None
        """
        logging.basicConfig(filename='logger.log', level=logging.INFO,
                            format = self.config['logger']['format'], filemode='w')