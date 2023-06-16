import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

class MailSender:
    def __init__(self,email,password,recievers_list,smtp):
        self.email = email
        self.password = password
        self.recievers = recievers_list
        self.smtp = smtp

        # Creating an instance of MIMEMultipart
        self.message = MIMEMultipart()

        # Assigning the sender_email, receiver_email, and subject of our mail
        self.message["From"] = self.email
        self.message['To'] = ", ".join(self.recievers)

    def set_cc(self,cc:list):
        self.message["Cc"] = ", ".join(cc)

    def set_header(self,header:str):
        self.message["Subject"] = header

    def set_mail_content(self,content:str):
        self.message.attach(MIMEText(content,'plain'))

    def set_mail_html_content(self,image_url,product_description):
        pass

    def send_email(self):
        #Converting message to string
        my_message = self.message.as_string()

        #Configuring SMTP
        email_session = smtplib.SMTP(self.smtp,587)
        email_session.starttls()
        email_session.login(self.email,self.password)
        email_session.sendmail(self.email,self.recievers,my_message)
        email_session.quit()
        print("Mail Sent")