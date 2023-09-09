from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.conf import settings
from django.core.exceptions import PermissionDenied
import os

def send_email(subject: str, message: str, to_list: list, pdf_file_path: str):
    from_email = settings.EMAIL_HOST_USER
    path = os.path.join(settings.BASE_DIR,pdf_file_path)
    if subject and message and from_email and to_list:
        try:
            email = EmailMessage(subject, message, from_email, to_list)
            if(pdf_file_path):
                with open(path, 'rb') as pdf_file:
                    email.attach(os.path.basename(path), pdf_file.read(), 'application/pdf')

            email.send()

            return HttpResponse("Mail Sent")
        except Exception as e:
            print(e)
            return HttpResponse(f"An error occurred: {str(e)}", status=500)
    else:
        raise PermissionDenied("Make sure all required fields are provided.")
    