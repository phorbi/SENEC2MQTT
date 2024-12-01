import logging
from logging.handlers import TimedRotatingFileHandler
log_file_name = 'SenecLog.log'
logging_level = logging.DEBUG

# set TimedRotatingFileHandler for root
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
# use very short interval for this example, typical 'when' would be 'midnight' and no explicit interval
handler = logging.handlers.TimedRotatingFileHandler(log_file_name, when="midnight", interval=1, backupCount=3)
handler.setFormatter(formatter)

logger = logging.getLogger() # or pass string to give it a name
logger.setLevel(logging_level)
logger.addHandler(handler)
