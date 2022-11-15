from __future__ import absolute_import, unicode_literals

from sys import exc_info

from .clients import SESClient
from innotter.celery import app


ses = SESClient


@app.task
def send_new_post_notification_email(subject: str, body: str, recipient_list: list) -> str:
    """
    Implement sending email to the page's followers. Return info of sending email.
    :param subject: subject of the email.
    :param body: body of the email.
    :param recipient_list: list of recipients.
    :return: corresponding result information.
    """
    try:
        ses.send_email(subject=subject, body=body, recipient_list=recipient_list)
        return 'The email(s) were successfully sent.'
    except Exception:
        return str(exc_info()[1])
