from __future__ import absolute_import, unicode_literals

from sys import exc_info
from smtplib import SMTPException

from django.core.mail import send_mail
from django.conf import settings

from innotter.celery import app


@app.task
def send_new_post_notification_email(subject: str, message: str, recipient_list: list) -> str:
    """
    Implement sending email to the page's followers. Return info of sending email.
    :param subject: subject of the sending.
    :param message: body of the email.
    :param recipient_list: list of recipients.
    :return: corresponding result information.
    """
    try:
        send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER,
                  recipient_list=recipient_list, fail_silently=False)
        return 'The email(s) were successfully sent.'
    except SMTPException:
        return str(exc_info()[1])
