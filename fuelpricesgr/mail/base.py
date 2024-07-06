"""Module containing base mail classes
"""
import logging

from fuelpricesgr import settings, storage

# The module logger
logger = logging.getLogger(__name__)


class MailSender:
    """Class for sending email messages
    """
    def __init__(self) -> None:
        """Create the mail sender object.
        """
        self.sender = None
        self.initialized = self.initialize()

    def initialize(self) -> bool:
        """Initialize the mail class.

        :return: True if the mail class was initialized.
        """
        if 'SENDER' in settings.MAIL:
            self.sender = settings.MAIL['SENDER']
        else:
            logger.error("Sender not set")

            return False

        return True

    @staticmethod
    def get_recipients() -> list[str]:
        """Get the recipients for the email. Returns the emails of the admin users.

        :return: The emails of the admin users.
        """
        with storage.get_storage() as s:
            return s.get_admin_user_emails()

    def send(self, subject: str, html_content: str):
        """Send an email.

        :param subject: The mail subject.
        :param html_content: The HTML content of the message.
        """
        if not self.initialized:
            return

        self.do_send(recipients=self.get_recipients(), subject=subject, html_content=html_content)

    def do_send(self, recipients: list[str], subject: str, html_content: str):
        """Send an email.

        :param recipients: The list of recipients.
        :param subject: The mail subject.
        :param html_content: The HTML content of the message.
        """