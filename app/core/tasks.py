"""Setup CRON task."""

from logging import getLogger
import json
import os
import datetime
import warnings
import re
from django.conf import settings
from app.celery import app
from core.services.mail_sender import send_email as send

warnings.filterwarnings('ignore', category=RuntimeWarning, module='django.db.models.fields')

logger = getLogger(__name__)


@app.task
def send_email(subject: str, message: str, to_list: list, pdf_file_path: str):
    send(subject, message, to_list, pdf_file_path)