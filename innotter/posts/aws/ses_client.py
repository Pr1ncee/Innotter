from django.conf import settings

from .base_client import ClientMeta


class SESClient(metaclass=ClientMeta):
    """
    Wrapper of AWS SES service using boto3.
    'send_email' class method sends email to list of recipient.
    """
    _service_name = 'ses'
    _client = None

    @classmethod
    def send_email(cls, subject: str, body: str, recipient_list: list) -> None:
        """
        Send email to particular email addresses
        :param subject: subject of the email
        :param body: body of the email
        :param recipient_list: list of recipients.
        :return: None.
        """
        cls.client.send_email(
            Source=settings.EMAIL_HOST_USER,
            Destination={
                'ToAddresses':
                    recipient_list
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Text': {
                        'Data': body
                    }
                },
            },
        )
