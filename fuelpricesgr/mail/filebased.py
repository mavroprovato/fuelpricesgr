"""Module containing classes for saving sent emails to a file
"""
import datetime
import email
import pathlib

from fuelpricesgr import mail, settings


class FileBasedMailSender(mail.MailSender):
    """Class for writing mails to a file. Used for development.
    """

    def __init__(self) -> None:
        """Create the file based mail sender.
        """
        super().__init__()

        self.mail_directory = settings.DATA_PATH / 'mails'
        self.mail_directory.mkdir(parents=True, exist_ok=True)

    def do_send(self, recipients: list[str], subject: str, html_content: str):
        """Send an email.

        :param subject: The mail subject.
        :param recipients: The list of recipients.
        :param html_content: The HTML content of the message.
        """
        message = email.message.EmailMessage()
        message['Subject'] = subject
        message['From'] = self.sender
        message['To'] = ','.join(recipients)
        message.add_header('Content-Type', 'text/html')
        message.set_payload(html_content)

        with self.get_filename().open('wt') as file:
            file.write(message.as_string())

    def get_filename(self) -> pathlib.Path:
        """Return the filename for the email.

        :return: The filename for the email.
        """
        return self.mail_directory / datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S.%f')
