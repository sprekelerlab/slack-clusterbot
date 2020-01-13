import time
import logging
from clusterbot import ClusterBot

# create logger to get library information
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# example code to send Denis Alevi a message
cb = ClusterBot(user_name='Denis Alevi')
cb.print("Starting example script.")
cb.print("Waiting for 5s.")
time.sleep(5)
cb.print("5s have passed. Closing. Thank you for flying with ClusterBot! :tada:")
