import logging
import random

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

OTP_EXPIRY_MINUTES = 10


def generate_otp():
    return str(random.randint(100000, 999999))


def set_email_otp(profile):
    """Generate OTP, persist it on the profile, and return the code."""
    otp = generate_otp()
    profile.two_factor_otp = otp
    profile.two_factor_otp_expiry = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    profile.save(update_fields=['two_factor_otp', 'two_factor_otp_expiry'])
    return otp


def verify_email_otp(profile, otp_code):
    """Return True if the OTP matches and has not expired."""
    if not profile.two_factor_otp or not profile.two_factor_otp_expiry:
        return False
    if profile.two_factor_otp != otp_code:
        return False
    if timezone.now() > profile.two_factor_otp_expiry:
        return False
    return True


def clear_email_otp(profile):
    profile.two_factor_otp = None
    profile.two_factor_otp_expiry = None
    profile.save(update_fields=['two_factor_otp', 'two_factor_otp_expiry'])


def send_2fa_otp_email(recipient_email, otp_code, username):
    """Send a 2FA OTP code via email."""
    try:
        context = {
            'otp_code': otp_code,
            'username': username,
            'expiry_minutes': OTP_EXPIRY_MINUTES,
        }
        html_content = render_to_string('accounts/emails/2fa_otp.html', context)
        text_content = (
            f'Your C3M verification code is: {otp_code}. '
            f'It expires in {OTP_EXPIRY_MINUTES} minutes.'
        )
        msg = EmailMultiAlternatives(
            subject='Your C3M Verification Code',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        logger.info(f'2FA OTP email sent to {recipient_email}')
        return True
    except Exception as e:
        logger.error(f'Failed to send 2FA OTP email to {recipient_email}: {str(e)}')
        return False
