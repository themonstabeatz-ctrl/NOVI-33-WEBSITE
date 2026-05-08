"""
Email service for booking confirmations and reminders
Supports multi-language: Serbian, English, Russian, Thai
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# Email configuration from environment
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'Bua Luang Thai Spa')

# Email templates in multiple languages
EMAIL_TEMPLATES = {
    'sr': {
        'confirmation_subject': 'Potvrda rezervacije - Bua Luang Thai Spa',
        'reminder_subject': 'Podsetnik za Vaš termin - Bua Luang Thai Spa',
        'confirmation_body': """
Poštovani/a {client_name},

Uspešno ste zakazali vaš tretman u Bua Luang Thai Spa!

📋 Detalji rezervacije:
━━━━━━━━━━━━━━━━━━━━━━
👤 Ime: {client_name}
📧 Email: {client_email}
📞 Telefon: {client_phone}
💆 Tretman: {service_name}
📅 Datum: {appointment_date}
🕐 Vreme: {appointment_time}
━━━━━━━━━━━━━━━━━━━━━━

📍 Lokacija: Abebe Bikile 10A, Beograd
🕐 Radno vreme: 10:00 - 22:00

ℹ️ VAŽNE INFORMACIJE:
• Molimo vas da stignete 10 minuta pre zakazanog termina
• Kasnjenje duže od 15 minuta može rezultovati skraćivanjem tretmana
• Za otkazivanje molimo kontaktirajte nas najmanje 4 sata unapred

Za sva pitanja kontaktirajte nas:
📧 bualuangthailandspa@gmail.com
📞 +381 62 625 500

Radujemo se vašoj poseti! 🌸

S poštovanjem,
Bua Luang Thai Spa Tim
""",
        'reminder_body': """
Poštovani/a {client_name},

Podsetnik: Imate zakazani tretman danas!

📋 Detalji rezervacije:
━━━━━━━━━━━━━━━━━━━━━━
👤 Ime: {client_name}
💆 Tretman: {service_name}
📅 Datum: {appointment_date}
🕐 Vreme: {appointment_time}
━━━━━━━━━━━━━━━━━━━━━━

📍 Lokacija: Abebe Bikile 10A, Beograd

⏰ Molimo vas da stignete 10 minuta pre zakazanog termina.

Vidimo se uskoro! 🌸

S poštovanjem,
Bua Luang Thai Spa Tim
"""
    },
    'en': {
        'confirmation_subject': 'Booking Confirmation - Bua Luang Thai Spa',
        'reminder_subject': 'Reminder: Your Treatment Today - Bua Luang Thai Spa',
        'confirmation_body': """
Dear {client_name},

You have successfully booked your treatment at Bua Luang Thai Spa!

📋 Booking Details:
━━━━━━━━━━━━━━━━━━━━━━
👤 Name: {client_name}
📧 Email: {client_email}
📞 Phone: {client_phone}
💆 Treatment: {service_name}
📅 Date: {appointment_date}
🕐 Time: {appointment_time}
━━━━━━━━━━━━━━━━━━━━━━

📍 Location: Abebe Bikile 10A, Belgrade
🕐 Working hours: 10:00 AM - 10:00 PM

ℹ️ IMPORTANT INFORMATION:
• Please arrive 10 minutes before your scheduled time
• Delays longer than 15 minutes may result in shortened treatment
• For cancellations, please contact us at least 4 hours in advance

For any questions, contact us:
📧 bualuangthailandspa@gmail.com
📞 +381 62 625 500

We look forward to your visit! 🌸

Best regards,
Bua Luang Thai Spa Team
""",
        'reminder_body': """
Dear {client_name},

Reminder: You have a scheduled treatment today!

📋 Booking Details:
━━━━━━━━━━━━━━━━━━━━━━
👤 Name: {client_name}
💆 Treatment: {service_name}
📅 Date: {appointment_date}
🕐 Time: {appointment_time}
━━━━━━━━━━━━━━━━━━━━━━

📍 Location: Abebe Bikile 10A, Belgrade

⏰ Please arrive 10 minutes before your scheduled time.

See you soon! 🌸

Best regards,
Bua Luang Thai Spa Team
"""
    },
    'ru': {
        'confirmation_subject': 'Подтверждение бронирования - Bua Luang Thai Spa',
        'reminder_subject': 'Напоминание: Ваша процедура сегодня - Bua Luang Thai Spa',
        'confirmation_body': """
Уважаемый/ая {client_name},

Вы успешно забронировали процедуру в Bua Luang Thai Spa!

📋 Детали бронирования:
━━━━━━━━━━━━━━━━━━━━━━
👤 Имя: {client_name}
📧 Email: {client_email}
📞 Телефон: {client_phone}
💆 Процедура: {service_name}
📅 Дата: {appointment_date}
🕐 Время: {appointment_time}
━━━━━━━━━━━━━━━━━━━━━━

📍 Адрес: Abebe Bikile 10A, Белград
🕐 Рабочие часы: 10:00 - 22:00

ℹ️ ВАЖНАЯ ИНФОРМАЦИЯ:
• Пожалуйста, приходите за 10 минут до назначенного времени
• Опоздание более 15 минут может привести к сокращению процедуры
• Для отмены, пожалуйста, свяжитесь с нами минимум за 4 часа

По всем вопросам свяжитесь с нами:
📧 bualuangthailandspa@gmail.com
📞 +381 62 625 500

Ждем вашего визита! 🌸

С уважением,
Команда Bua Luang Thai Spa
""",
        'reminder_body': """
Уважаемый/ая {client_name},

Напоминание: У вас запланирована процедура сегодня!

📋 Детали бронирования:
━━━━━━━━━━━━━━━━━━━━━━
👤 Имя: {client_name}
💆 Процедура: {service_name}
📅 Дата: {appointment_date}
🕐 Время: {appointment_time}
━━━━━━━━━━━━━━━━━━━━━━

📍 Адрес: Abebe Bikile 10A, Белград

⏰ Пожалуйста, приходите за 10 минут до назначенного времени.

До скорой встречи! 🌸

С уважением,
Команда Bua Luang Thai Spa
"""
    },
    'th': {
        'confirmation_subject': 'ยืนยันการจอง - Bua Luang Thai Spa',
        'reminder_subject': 'เตือนความจำ: การนวดของคุณวันนี้ - Bua Luang Thai Spa',
        'confirmation_body': """
เรียน {client_name},

คุณได้จองการนวดที่ Bua Luang Thai Spa สำเร็จแล้ว!

📋 รายละเอียดการจอง:
━━━━━━━━━━━━━━━━━━━━━━
👤 ชื่อ: {client_name}
📧 อีเมล: {client_email}
📞 โทรศัพท์: {client_phone}
💆 การบริการ: {service_name}
📅 วันที่: {appointment_date}
🕐 เวลา: {appointment_time}
━━━━━━━━━━━━━━━━━━━━━━

📍 สถานที่: Abebe Bikile 10A, Belgrade
🕐 เวลาทำการ: 10:00 - 22:00

ℹ️ ข้อมูลสำคัญ:
• กรุณามาถึง 10 นาทีก่อนเวลานัดหมาย
• การมาสายเกิน 15 นาทีอาจทำให้เวลาบริการสั้นลง
• สำหรับการยกเลิก กรุณาติดต่อเราอย่างน้อย 4 ชั่วโมงล่วงหน้า

หากมีคำถาม ติดต่อเรา:
📧 bualuangthailandspa@gmail.com
📞 +381 62 625 500

เรารอคอยการมาเยือนของคุณ! 🌸

ด้วยความเคารพ,
ทีม Bua Luang Thai Spa
""",
        'reminder_body': """
เรียน {client_name},

เตือนความจำ: คุณมีนัดหมายการนวดวันนี้!

📋 รายละเอียดการจอง:
━━━━━━━━━━━━━━━━━━━━━━
👤 ชื่อ: {client_name}
💆 การบริการ: {service_name}
📅 วันที่: {appointment_date}
🕐 เวลา: {appointment_time}
━━━━━━━━━━━━━━━━━━━━━━

📍 สถานที่: Abebe Bikile 10A, Belgrade

⏰ กรุณามาถึง 10 นาทีก่อนเวลานัดหมาย

แล้วพบกันเร็วๆ นี้! 🌸

ด้วยความเคารพ,
ทีม Bua Luang Thai Spa
"""
    }
}


def format_date_time(iso_datetime: str, language: str = 'sr') -> tuple:
    """Format datetime for display based on language"""
    try:
        dt = datetime.fromisoformat(iso_datetime.replace('Z', '+00:00'))
        
        # Format date based on language
        if language == 'sr':
            date_str = dt.strftime('%d.%m.%Y')  # DD.MM.YYYY
            time_str = dt.strftime('%H:%M')
        elif language == 'en':
            date_str = dt.strftime('%B %d, %Y')  # January 02, 2025
            time_str = dt.strftime('%I:%M %p')  # 02:00 PM
        elif language == 'ru':
            date_str = dt.strftime('%d.%m.%Y')  # DD.MM.YYYY
            time_str = dt.strftime('%H:%M')
        elif language == 'th':
            date_str = dt.strftime('%d.%m.%Y')  # DD.MM.YYYY
            time_str = dt.strftime('%H:%M')
        else:
            date_str = dt.strftime('%d.%m.%Y')
            time_str = dt.strftime('%H:%M')
            
        return date_str, time_str
    except Exception as e:
        logger.error(f"Error formatting datetime: {e}")
        return iso_datetime.split('T')[0], iso_datetime.split('T')[1][:5]


def send_email(to_email: str, subject: str, body: str, html_body: str = None) -> bool:
    """Send email via Gmail SMTP with optional HTML"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach plain text body (fallback)
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Attach HTML body if provided
        if html_body:
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # Remove any spaces from password
        smtp_password = SMTP_PASSWORD.replace(' ', '')
        
        # Connect to Gmail SMTP
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, smtp_password)
            server.send_message(msg)
        
        logger.info(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
        return False


def create_html_email_template(
    client_name: str,
    content: str,
    language: str = 'sr'
) -> str:
    """Create beautiful HTML email template with spa theme"""
    
    greeting_text = {
        'sr': f'Poštovani/a {client_name},',
        'en': f'Dear {client_name},',
        'ru': f'Уважаемый/ая {client_name},',
        'th': f'เรียนคุณ {client_name},'
    }
    
    footer_text = {
        'sr': 'S poštovanjem, Bua Luang Thai Spa Tim',
        'en': 'Best regards, Bua Luang Thai Spa Team',
        'ru': 'С уважением, Команда Bua Luang Thai Spa',
        'th': 'ด้วยความเคารพ, ทีม Bua Luang Thai Spa'
    }
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
            }}
            .email-container {{
                max-width: 500px;
                margin: 10px auto;
                background: #ffffff;
                border: 1px solid #d4af37;
                border-radius: 5px;
                overflow: hidden;
            }}
            .header {{
                background-image: url('https://customer-assets.emergentagent.com/job_massage-hub-10/artifacts/u7h8apz4_podloga.jpg');
                background-size: cover;
                background-position: center;
                padding: 15px;
                text-align: center;
                border-bottom: 2px solid #d4af37;
                position: relative;
            }}
            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.6);
                z-index: 1;
            }}
            .header-content {{
                position: relative;
                z-index: 2;
            }}
            .logo {{
                width: 60px;
                height: auto;
                margin-bottom: 5px;
            }}
            .header-title {{
                color: #d4af37;
                font-size: 10px;
                font-weight: bold;
                margin: 0;
            }}
            .content {{
                padding: 12px;
                color: #333333;
                line-height: 1.3;
                font-size: 9px;
                background-image: url('https://customer-assets.emergentagent.com/job_massage-hub-10/artifacts/u7h8apz4_podloga.jpg');
                background-size: cover;
                background-position: center;
                position: relative;
            }}
            .content::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(255, 255, 255, 0.92);
                z-index: 1;
            }}
            .content > * {{
                position: relative;
                z-index: 2;
            }}
            .greeting {{
                font-size: 9px;
                color: #d4af37;
                margin-bottom: 6px;
                font-weight: bold;
            }}
            .details-box {{
                background: rgba(250, 250, 250, 0.95);
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px;
                margin: 6px 0;
            }}
            .detail-row {{
                display: flex;
                justify-content: space-between;
                margin: 3px 0;
                padding: 2px 0;
                border-bottom: 1px solid #f0f0f0;
                font-size: 8px;
            }}
            .detail-row:last-child {{
                border-bottom: none;
            }}
            .detail-label {{
                color: #666666;
                font-weight: 600;
            }}
            .detail-value {{
                color: #333333;
                text-align: right;
            }}
            .info-text {{
                background: rgba(255, 254, 248, 0.95);
                border-left: 2px solid #d4af37;
                padding: 5px;
                margin: 6px 0;
                font-size: 8px;
                color: #555555;
            }}
            .contact-info {{
                text-align: center;
                padding: 6px;
                font-size: 8px;
                color: #666666;
            }}
            .contact-info a {{
                color: #d4af37;
                text-decoration: none;
            }}
            .footer {{
                background: #1a1506;
                padding: 6px;
                text-align: center;
                border-top: 2px solid #d4af37;
                color: #d4af37;
                font-size: 8px;
            }}
            @media only screen and (max-width: 500px) {{
                .email-container {{
                    margin: 0;
                    border-radius: 0;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="header-content">
                    <img src="https://customer-assets.emergentagent.com/job_massage-hub-10/artifacts/55jx0bj4_Bua%20luang%20logo%20crna%20senka.png" alt="Logo" class="logo">
                    <div class="header-title">Bua Luang Thai Spa</div>
                </div>
            </div>
            
            <div class="content">
                <div class="greeting">{greeting_text.get(language, greeting_text['sr'])}</div>
                
                {content}
                
                <div class="contact-info">
                    📧 <a href="mailto:bualuangthailandspa@gmail.com">bualuangthailandspa@gmail.com</a><br>
                    📞 <a href="tel:+381626255500">+381 62 625 500</a> | 📍 Abebe Bikile 10A<br>
                    🌸
                </div>
            </div>
            
            <div class="footer">
                {footer_text.get(language, footer_text['sr'])}
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def send_confirmation_email(
    client_email: str,
    client_name: str,
    client_phone: str,
    service_name: str,
    appointment_datetime: str,
    language: str = 'sr'
) -> bool:
    """Send booking confirmation email with beautiful HTML"""
    try:
        logger.info(f"📧 Sending CONFIRMATION email to {client_email} in language: {language}")
        
        # Get template for language (default to Serbian if not found)
        template = EMAIL_TEMPLATES.get(language, EMAIL_TEMPLATES['sr'])
        
        # Format date and time
        date_str, time_str = format_date_time(appointment_datetime, language)
        
        # Multilingual content
        translations = {
            'sr': {
                'success': '✅ Uspešno zakazano!',
                'treatment': '💆 Tretman:',
                'date': '📅 Datum:',
                'time': '🕐 Vreme:',
                'name': '👤 Ime:',
                'phone': '📞 Telefon:',
                'info': 'Stignite 10 min pre termina. Otkazivanje 4h unapred.'
            },
            'en': {
                'success': '✅ Successfully Booked!',
                'treatment': '💆 Treatment:',
                'date': '📅 Date:',
                'time': '🕐 Time:',
                'name': '👤 Name:',
                'phone': '📞 Phone:',
                'info': 'Arrive 10 min before. Cancellation 4h in advance.'
            },
            'ru': {
                'success': '✅ Успешно забронировано!',
                'treatment': '💆 Процедура:',
                'date': '📅 Дата:',
                'time': '🕐 Время:',
                'name': '👤 Имя:',
                'phone': '📞 Телефон:',
                'info': 'Приходите за 10 мин. Отмена за 4ч.'
            },
            'th': {
                'success': '✅ จองสำเร็จ!',
                'treatment': '💆 การรักษา:',
                'date': '📅 วันที่:',
                'time': '🕐 เวลา:',
                'name': '👤 ชื่อ:',
                'phone': '📞 โทรศัพท์:',
                'info': 'มาก่อน 10 นาที ยกเลิกก่อน 4 ชม.'
            }
        }
        
        content = translations.get(language, translations['sr'])
        
        # SHORT plain text for email preview only
        subject = template['confirmation_subject']
        plain_body = f"{content['success']} {client_name} - {service_name}, {date_str} {time_str}."
        
        # Create HTML content with smaller fonts (9px instead of 11px)
        html_content = f"""
        <p style="font-size: 9px; color: #d4af37; margin: 0 0 5px 0;">
            <strong>{content['success']}</strong>
        </p>
        
        <div class="details-box">
            <div class="detail-row">
                <span class="detail-label">{content['treatment']}</span>
                <span class="detail-value">{service_name}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">{content['date']}</span>
                <span class="detail-value">{date_str}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">{content['time']}</span>
                <span class="detail-value">{time_str}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">{content['name']}</span>
                <span class="detail-value">{client_name}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">{content['phone']}</span>
                <span class="detail-value">{client_phone}</span>
            </div>
        </div>
        
        <div class="info-text">
            {content['info']}
        </div>
        """
        
        html_body = create_html_email_template(client_name, html_content, language)
        
        return send_email(client_email, subject, plain_body, html_body)
        
    except Exception as e:
        logger.error(f"Error sending confirmation email: {e}")
        return False


def send_reminder_email(
    client_email: str,
    client_name: str,
    service_name: str,
    appointment_datetime: str,
    language: str = 'sr'
) -> bool:
    """Send appointment reminder email with beautiful HTML - Bua Luang Style"""
    try:
        logger.info(f"📧 Sending REMINDER email to {client_email} in language: {language}")
        
        # Get template for language (default to Serbian if not found)
        template = EMAIL_TEMPLATES.get(language, EMAIL_TEMPLATES['sr'])
        
        # Format date and time
        date_str, time_str = format_date_time(appointment_datetime, language)
        
        # Multilingual content
        translations = {
            'sr': {
                'title': '⏰ Podsetnik za Vaš Termin',
                'greeting': f'Poštovani/a {client_name},',
                'message1': 'Podsećamo Vas da Vaš termin za masažu počinje za oko 2 sata.',
                'message2': 'Molimo Vas da dođete 5–10 minuta ranije kako bismo sve pripremili na vreme.',
                'message3': 'U slučaju kašnjenja ili potrebe za odlaganjem molimo vas obavestite nas.',
                'treatment': '💆 Tretman',
                'date': '📅 Datum',
                'time': '🕐 Vreme',
                'location_label': '📍 Lokacija',
                'location_value': 'Abebe Bikile 10A, Zemun',
                'closing': '✨ Radujemo se Vašoj poseti! ✨',
                'regards': 'S poštovanjem,<br>Bua Luang Thai Spa Tim'
            },
            'en': {
                'title': '⏰ Reminder: Your Treatment Today',
                'greeting': f'Dear {client_name},',
                'message1': 'This is a reminder that your massage treatment starts in approximately 2 hours.',
                'message2': 'Please arrive 5–10 minutes early so we can prepare everything on time.',
                'message3': 'In case of delay or need to reschedule, please let us know.',
                'treatment': '💆 Treatment',
                'date': '📅 Date',
                'time': '🕐 Time',
                'location_label': '📍 Location',
                'location_value': 'Abebe Bikile 10A, Zemun',
                'closing': '✨ We look forward to seeing you! ✨',
                'regards': 'Best regards,<br>Bua Luang Thai Spa Team'
            },
            'ru': {
                'title': '⏰ Напоминание о Вашем Сеансе',
                'greeting': f'Уважаемый/ая {client_name},',
                'message1': 'Напоминаем, что Ваш сеанс массажа начинается примерно через 2 часа.',
                'message2': 'Пожалуйста, приходите на 5–10 минут раньше, чтобы мы могли все подготовить вовремя.',
                'message3': 'В случае задержки или необходимости переноса, пожалуйста, сообщите нам.',
                'treatment': '💆 Процедура',
                'date': '📅 Дата',
                'time': '🕐 Время',
                'location_label': '📍 Адрес',
                'location_value': 'Abebe Bikile 10A, Земун',
                'closing': '✨ Ждем Вас с нетерпением! ✨',
                'regards': 'С уважением,<br>Команда Bua Luang Thai Spa'
            },
            'th': {
                'title': '⏰ เตือนความจำ: การนัดหมายของคุณวันนี้',
                'greeting': f'เรียนคุณ {client_name},',
                'message1': 'นี่คือการเตือนความจำว่าการนวดของคุณจะเริ่มในอีกประมาณ 2 ชั่วโมง',
                'message2': 'กรุณามาถึงก่อนเวลา 5-10 นาทีเพื่อให้เราได้เตรียมทุกอย่างทันเวลา',
                'message3': 'หากล่าช้าหรือต้องการเลื่อนนัด กรุณาแจ้งให้เราทราบ',
                'treatment': '💆 การรักษา',
                'date': '📅 วันที่',
                'time': '🕐 เวลา',
                'location_label': '📍 สถานที่',
                'location_value': 'Abebe Bikile 10A, Zemun',
                'closing': '✨ เรารอคอยที่จะพบคุณ! ✨',
                'regards': 'ด้วยความนับถือ<br>ทีม Bua Luang Thai Spa'
            }
        }
        
        content = translations.get(language, translations['sr'])
        
        # SHORT plain text for email preview only
        subject = template['reminder_subject']
        plain_body = f"{content['title']}: {client_name}, {time_str} - {service_name}."
        
        # Create LUXURY HTML content for reminder - Golden text on dark elegant background
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Georgia', serif;
                    background-color: #0a0a0a;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background: linear-gradient(135deg, #1a1506 0%, #2d2410 100%);
                    border: 2px solid #d4af37;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 8px 24px rgba(212, 175, 55, 0.3);
                }}
                .header {{
                    background-image: url('https://customer-assets.emergentagent.com/job_massage-hub-10/artifacts/u7h8apz4_podloga.jpg');
                    background-size: cover;
                    background-position: center;
                    padding: 15px 10px;
                    text-align: center;
                    border-bottom: 2px solid #d4af37;
                    position: relative;
                }}
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(10, 10, 10, 0.85);
                    z-index: 1;
                }}
                .header-content {{
                    position: relative;
                    z-index: 2;
                }}
                .logo {{
                    width: 40px;
                    height: auto;
                    margin-bottom: 5px;
                    filter: drop-shadow(0 1px 4px rgba(212, 175, 55, 0.6));
                }}
                .header-title {{
                    color: #d4af37;
                    font-size: 8px;
                    font-weight: bold;
                    margin: 3px 0;
                    text-shadow: 0 2px 8px rgba(212, 175, 55, 0.4);
                    letter-spacing: 0.5px;
                }}
                .header-subtitle {{
                    color: #c9a961;
                    font-size: 6px;
                    margin: 2px 0;
                    font-style: italic;
                }}
                .content {{
                    padding: 10px 8px;
                    background: linear-gradient(to bottom, #1a1506 0%, #0f0f0a 100%);
                    position: relative;
                }}
                .greeting {{
                    font-size: 7px;
                    color: #d4af37;
                    margin-bottom: 5px;
                    font-weight: bold;
                    text-align: center;
                    text-shadow: 0 1px 4px rgba(212, 175, 55, 0.3);
                }}
                .message {{
                    color: #e6d5b8;
                    font-size: 6px;
                    line-height: 1.2;
                    margin: 3px 0;
                    text-align: center;
                }}
                .highlight {{
                    color: #d4af37;
                    font-weight: bold;
                }}
                .details-box {{
                    background: rgba(212, 175, 55, 0.1);
                    border: 1px solid #d4af37;
                    border-radius: 6px;
                    padding: 8px;
                    margin: 10px 0;
                    box-shadow: inset 0 1px 4px rgba(0, 0, 0, 0.3);
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 4px 0;
                    padding: 4px 0;
                    border-bottom: 1px solid rgba(212, 175, 55, 0.3);
                }}
                .detail-row:last-child {{
                    border-bottom: none;
                }}
                .detail-label {{
                    color: #c9a961;
                    font-weight: 600;
                    font-size: 6px;
                }}
                .detail-value {{
                    color: #d4af37;
                    text-align: right;
                    font-size: 6px;
                    font-weight: bold;
                }}
                .closing {{
                    color: #d4af37;
                    font-size: 7px;
                    text-align: center;
                    margin-top: 6px;
                    font-weight: bold;
                    text-shadow: 0 1px 4px rgba(212, 175, 55, 0.3);
                }}
                .contact-info {{
                    text-align: center;
                    padding: 6px;
                    font-size: 5px;
                    color: #c9a961;
                    border-top: 1px solid rgba(212, 175, 55, 0.3);
                    margin-top: 6px;
                    line-height: 1.2;
                }}
                .contact-info a {{
                    color: #d4af37;
                    text-decoration: none;
                    font-weight: bold;
                }}
                .footer {{
                    background: #0a0a0a;
                    padding: 5px;
                    text-align: center;
                    border-top: 1px solid #d4af37;
                    color: #d4af37;
                    font-size: 5px;
                    font-style: italic;
                    line-height: 1.2;
                }}
                .divider {{
                    height: 1px;
                    background: linear-gradient(to right, transparent, #d4af37, transparent);
                    margin: 6px 0;
                }}
                @media only screen and (max-width: 600px) {{
                    .email-container {{
                        margin: 0;
                        border-radius: 0;
                    }}
                    .content {{
                        padding: 30px 20px;
                    }}
                    .detail-row {{
                        flex-direction: column;
                        text-align: center;
                    }}
                    .detail-value {{
                        text-align: center;
                        margin-top: 5px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="header-content">
                        <img src="https://customer-assets.emergentagent.com/job_massage-hub-10/artifacts/55jx0bj4_Bua%20luang%20logo%20crna%20senka.png" alt="Logo" class="logo">
                        <div class="header-title">{content['title']}</div>
                        <div class="header-subtitle">Bua Luang Thai Spa</div>
                    </div>
                </div>
                
                <div class="content">
                    <div class="greeting">{content['greeting']}</div>
                    
                    <div class="divider"></div>
                    
                    <p class="message">
                        {content['message1']}
                    </p>
                    
                    <p class="message">
                        {content['message2']}
                    </p>
                    
                    <p class="message">
                        {content['message3']}
                    </p>
                    
                    <div class="divider"></div>
                    
                    <div class="details-box">
                        <div class="detail-row">
                            <span class="detail-label">{content['treatment']}</span>
                            <span class="detail-value">{service_name}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">{content['date']}</span>
                            <span class="detail-value">{date_str}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">{content['time']}</span>
                            <span class="detail-value">{time_str}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">{content['location_label']}</span>
                            <span class="detail-value">{content['location_value']}</span>
                        </div>
                    </div>
                    
                    <div class="closing">
                        {content['closing']}
                    </div>
                    
                    <div class="contact-info">
                        📧 <a href="mailto:bualuangthailandspa@gmail.com">bualuangthailandspa@gmail.com</a><br>
                        📞 <a href="tel:+381626255500">+381 62 625 500</a><br>
                        🌸
                    </div>
                </div>
                
                <div class="footer">
                    {content['regards']}
                </div>
            </div>
        </body>
        </html>
        """
        
        return send_email(client_email, subject, plain_body, html_body)
        
    except Exception as e:
        logger.error(f"Error sending reminder email: {e}")
        return False
