from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from django.conf import settings
import os

def generate(filename:str,data:list,transaction_id):
    # try:
    path = os.path.join(settings.INVOICES_PATH,filename)
    doc = SimpleDocTemplate(path, pagesize=letter)

    elements = []

    company_name = "GoShopNow"

    custom_style = ParagraphStyle(
        name='CustomTitle',
        fontName='Helvetica',
        fontSize=28,
        textColor=colors.blue,
        alignment=1,
        encoding='utf-8',
    )
    centered = Paragraph(company_name, custom_style)
    elements.append(centered)

    custom_style = ParagraphStyle(
        name='CustomTitle',
        fontSize=8,
    )
    new_data = []
    for _ in data:
            new_data.append([Paragraph(_[0],custom_style),_[1],_[2],_[3]])

    table = Table(new_data, colWidths=[200, 80, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Courier'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTENCODING', (1, 0), (-1, -1), 'utf-8'),
    ]))


    data_total = [
        ["", "", "", "Total"],
        ["", "", "", f"Total: ${sum([float(row[-1]) for row in new_data[1:]])}"],
    ]
    table_total = Table(data_total, colWidths=[200, 80, 80, 80])
    table_total.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(Spacer(1, 0.25 * inch))

    today = 'Date: '+datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_style = ParagraphStyle(name='DateStyle', alignment=2)  # 2 corresponds to right alignment
    date_text = Paragraph(today, date_style)
    elements.append(date_text)
    elements.append(Spacer(1, 0.15 * inch))

    custom_style = ParagraphStyle(
        name='CustomTitle',
        fontSize=20,
        alignment=1,
    )

    centered = Paragraph('Payment Invoice', custom_style)
    elements.append(centered)

    custom_style = ParagraphStyle(
        name='CustomTitle',
        fontSize=12,
        alignment=0,
    )
    elements.append(Spacer(1, 0.15 * inch))
    centered = Paragraph("Transaction ID: "+ transaction_id, custom_style)
    elements.append(centered)

    elements.append(Spacer(1, 0.15 * inch))

    elements.append(table)
    elements.append(table_total)

    doc.build(elements)
    #     return True
    # except:
    #     return False