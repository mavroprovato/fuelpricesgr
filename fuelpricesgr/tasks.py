"""The tasks module.
"""
import logging

from fuelpricesgr import importer

# The module logger
logger = logging.getLogger(__name__)


def import_data():
    """Import data.
    """
    logger.info('Importing data')
    importer.import_data()
