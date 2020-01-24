import logging
from .clusterbot import ClusterBot

logging.getLogger(__name__).addHandler(logging.NullHandler())



def activate_logger(loglevel='INFO'):
    """
    Print log messages during executions.

    Parameters
    ----------
    loglevel : {'INFO', 'DEBUG'}
        Loglevel string. 'INFO' logs sent messages. 'DEBUG' activates debug
        mode.
    """
    # create logger to get library information
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, loglevel))
