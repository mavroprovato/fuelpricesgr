"""Module containing Amazon SES classes
"""
import logging

import boto3

from fuelpricesgr import mail, settings

# The module logger
logger = logging.getLogger(__name__)


class SESMailSender(mail.MailSender):
    """Class for sending email messages with Amazon SES
    """
    def __init__(self) -> None:
        """Create the Amazon SES email sender
        """
        super().__init__()

        self.client = boto3.client('ses', region_name=settings.MAIL['PARAMETERS']['AWS_REGION'])

    def send(self, subject: str, html_content: str):
        """Send an email.

        :param subject: The mail subject.
        :param html_content: The HTML content of the message.
        """
        if not self.recipients:
            logger.error("No recipients to send the email")
            return

        self.client.send_email(
            Destination={'ToAddresses': self.recipients},
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
