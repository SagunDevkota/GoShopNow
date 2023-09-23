from django.core.mail import EmailMessage
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os

def send_email(subject: str, message: str, to_list: list, pdf_file_path: str):
    from_email = settings.EMAIL_HOST_USER
    path = os.path.join(settings.INVOICES_PATH,pdf_file_path)
    if subject and message and from_email and to_list:
        try:
            email = EmailMessage(subject, message, from_email, to_list)
            if(pdf_file_path):
                with open(path, 'rb') as pdf_file:
                    email.attach(os.path.basename(path), pdf_file.read(), 'application/pdf')

            email.send()

            return True
        except Exception as e:
            print(e)
            return False
    else:
        return False
    