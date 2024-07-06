"""Module containing base mail classes
"""
from fuelpricesgr import settings, storage


class MailSender:
    """Class for sending email messages
    """
    def __init__(self) -> None:
        """Create the mail sender object.
        """
        self.sender = settings.MAIL['SENDER']
        self.recipients = self.get_recipients()

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
        return NotImplementedError()
