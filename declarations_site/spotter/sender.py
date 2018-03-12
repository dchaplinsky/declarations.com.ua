from time import sleep
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives


def send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None, html_message=None, timeout=None, max_retries=3, retry_wait=1):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.
    """
    for i in range(max_retries):
        try:
            connection = connection or get_connection(
                username=auth_user,
                password=auth_password,
                fail_silently=fail_silently,
                timeout=timeout
            )
            mail = EmailMultiAlternatives(subject, message, from_email, recipient_list, connection=connection)
            if html_message:
                mail.attach_alternative(html_message, 'text/html')

            return mail.send()

        except Exception:
            if i >= max_retries - 1:
                raise
            if retry_wait:
                sleep(retry_wait)
