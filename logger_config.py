import logging

# Logger Module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

info_handler = logging.FileHandler('app.log')
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

error_handler = logging.FileHandler('app.log')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

critical_handler = logging.FileHandler("app.log")
critical_handler.setLevel(logging.CRITICAL)
critical_handler.setFormatter(formatter)

if logger.hasHandlers():
    logger.handlers.clear()

# Add handlers to the logger
logger.addHandler(info_handler)
logger.addHandler(error_handler)
logger.addHandler(critical_handler)
