"""Module containing mail related methods
"""
import logging

import boto3

from . import settings

# The module logger
logger = logging.getLogger(__name__)


class MailSender:
    """Class for sending email messages
    """
    def __init__(self) -> None:
        """Create the mail sender object.
        """
        if settings.AWS_REGION:
            self.client = boto3.client('ses', region_name=settings.AWS_REGION)
        else:
            self.client = None
        self.sender = settings.MAIL_SENDER

    def is_configured(self) -> bool:
        """Check if the sender is configured correctly to send emails.

        :return: True if the object is configured correctly, False otherwise.
        """
        if not self.client:
            logger.error("Could not create client")
            return False
        if not self.sender:
            logger.error("Sender not set")
            return False

        return True

    def send(self, to_recipients: list[str], subject: str, html_content: str) -> None:
        """Send an email.

        :param to_recipients: A list of To: recipients.
        :param subject: The mail subject.
        :param html_content: The HTML content of the message.
        """
        if not self.is_configured():
            return

        self.client.send_email(
            Destination={'ToAddresses': to_recipients},
            Message={
                'Body': {
                    'Html': {
                        'Data': html_content,
                    }
                },
                'Subject': {
                    'Data': subject,
                },
            },
            Source=self.sender
        )
