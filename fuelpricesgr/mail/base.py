"""Module containing mail related methods
"""
import logging

import boto3

from fuelpricesgr import settings, storage

# The module logger
logger = logging.getLogger(__name__)


class MailSender:
    """Class for sending email messages
    """
    def __init__(self) -> None:
        """Create the mail sender object.
        """
        self.client = boto3.client('ses', region_name=settings.AWS_REGION)
        self.sender = settings.MAIL_SENDER

    def send(self, subject: str, html_content: str) -> None:
        """Send an email.

        :param subject: The mail subject.
        :param html_content: The HTML content of the message.
        """
        with storage.get_storage() as s:
            recipients = s.get_admin_user_emails()

        if not recipients:
            logger.error("No recipients to send the email")
            return

        self.client.send_email(
            Destination={'ToAddresses': recipients},
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
