import logging

# Logging setup
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def log_message(message):
    print(message)
    logging.info(message) 