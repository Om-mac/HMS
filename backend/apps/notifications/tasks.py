"""
Celery tasks for notification handling.
"""
from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_appointment_confirmation(self, appointment_id: str):
    """
    Send appointment confirmation notification via WhatsApp.
    """
    from apps.appointments.models import Appointment
    from apps.notifications.models import Notification, NotificationTemplate
    from apps.notifications.whatsapp import whatsapp_service
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        patient = appointment.patient
        doctor = appointment.doctor
        
        # Get or create template
        template, _ = NotificationTemplate.objects.get_or_create(
            template_type='appointment_confirmation',
            defaults={
                'name': 'Appointment Confirmation',
                'channel': 'whatsapp',
                'body': '''🏥 *Appointment Confirmed*

Dear {{patient_name}},

Your appointment has been scheduled:

👨‍⚕️ Doctor: Dr. {{doctor_name}}
📅 Date: {{date}}
⏰ Time: {{time}}
🏢 Clinic: {{clinic_name}}
📍 Address: {{clinic_address}}
🎫 Token: #{{token_number}}

Please arrive 15 minutes early.

Reply CANCEL to cancel or RESCHEDULE to change timing.''',
                'available_variables': [
                    'patient_name', 'doctor_name', 'date', 'time',
                    'clinic_name', 'clinic_address', 'token_number'
                ]
            }
        )
        
        # Prepare message context
        context = {
            'patient_name': patient.user.full_name,
            'doctor_name': doctor.user.full_name,
            'date': appointment.appointment_date.strftime('%A, %B %d, %Y'),
            'time': appointment.start_time.strftime('%I:%M %p'),
            'clinic_name': appointment.clinic.name,
            'clinic_address': appointment.clinic.address,
            'token_number': appointment.token_number or 'TBD'
        }
        
        message = template.render(context)
        recipient_number = patient.user.whatsapp_number or patient.user.phone_number
        
        if not recipient_number:
            logger.warning(f"No phone number for patient {patient.id}")
            return
        
        # Send WhatsApp message
        result = whatsapp_service.send_message(recipient_number, message)
        
        # Log notification
        notification = Notification.objects.create(
            template=template,
            recipient=patient.user,
            channel='whatsapp',
            recipient_contact=recipient_number,
            body=message,
            appointment=appointment,
            status='sent' if result['success'] else 'failed',
            external_id=result.get('message_id', ''),
            error_message=result.get('error', ''),
            sent_at=timezone.now() if result['success'] else None
        )
        
        logger.info(f"Appointment confirmation sent: {notification.id}")
        
    except Appointment.DoesNotExist:
        logger.error(f"Appointment not found: {appointment_id}")
    except Exception as e:
        logger.error(f"Failed to send confirmation: {str(e)}")
        self.retry(countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_appointment_reschedule_notification(self, appointment_id: str):
    """
    Send appointment reschedule notification to both patient and doctor.
    """
    from apps.appointments.models import Appointment
    from apps.notifications.models import Notification, NotificationTemplate
    from apps.notifications.whatsapp import whatsapp_service
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        patient = appointment.patient
        doctor = appointment.doctor
        
        template, _ = NotificationTemplate.objects.get_or_create(
            template_type='appointment_reschedule',
            defaults={
                'name': 'Appointment Rescheduled',
                'channel': 'whatsapp',
                'body': '''📅 *Appointment Rescheduled*

Dear {{recipient_name}},

Your appointment has been rescheduled:

*Previous:* {{original_date}} at {{original_time}}
*New:* {{new_date}} at {{new_time}}

👨‍⚕️ Doctor: Dr. {{doctor_name}}
🏢 Clinic: {{clinic_name}}

Reason: {{reason}}

Reply CONFIRM to accept or call us to discuss.''',
                'available_variables': [
                    'recipient_name', 'original_date', 'original_time',
                    'new_date', 'new_time', 'doctor_name', 'clinic_name', 'reason'
                ]
            }
        )
        
        # Send to patient
        patient_context = {
            'recipient_name': patient.user.full_name,
            'original_date': appointment.original_date.strftime('%B %d, %Y') if appointment.original_date else 'N/A',
            'original_time': appointment.original_time.strftime('%I:%M %p') if appointment.original_time else 'N/A',
            'new_date': appointment.appointment_date.strftime('%B %d, %Y'),
            'new_time': appointment.start_time.strftime('%I:%M %p'),
            'doctor_name': doctor.user.full_name,
            'clinic_name': appointment.clinic.name,
            'reason': appointment.reschedule_reason or 'Schedule adjustment'
        }
        
        patient_number = patient.user.whatsapp_number or patient.user.phone_number
        if patient_number:
            message = template.render(patient_context)
            result = whatsapp_service.send_message(patient_number, message)
            
            Notification.objects.create(
                template=template,
                recipient=patient.user,
                channel='whatsapp',
                recipient_contact=patient_number,
                body=message,
                appointment=appointment,
                status='sent' if result['success'] else 'failed',
                external_id=result.get('message_id', ''),
                sent_at=timezone.now() if result['success'] else None
            )
        
        # Send to doctor
        doctor_context = {
            'recipient_name': f"Dr. {doctor.user.full_name}",
            'original_date': appointment.original_date.strftime('%B %d, %Y') if appointment.original_date else 'N/A',
            'original_time': appointment.original_time.strftime('%I:%M %p') if appointment.original_time else 'N/A',
            'new_date': appointment.appointment_date.strftime('%B %d, %Y'),
            'new_time': appointment.start_time.strftime('%I:%M %p'),
            'doctor_name': doctor.user.full_name,
            'clinic_name': appointment.clinic.name,
            'reason': f"Patient: {patient.user.full_name}"
        }
        
        doctor_number = doctor.user.whatsapp_number or doctor.user.phone_number
        if doctor_number:
            message = template.render(doctor_context)
            result = whatsapp_service.send_message(doctor_number, message)
            
            Notification.objects.create(
                template=template,
                recipient=doctor.user,
                channel='whatsapp',
                recipient_contact=doctor_number,
                body=message,
                appointment=appointment,
                status='sent' if result['success'] else 'failed',
                external_id=result.get('message_id', ''),
                sent_at=timezone.now() if result['success'] else None
            )
        
        logger.info(f"Reschedule notifications sent for appointment: {appointment_id}")
        
    except Appointment.DoesNotExist:
        logger.error(f"Appointment not found: {appointment_id}")
    except Exception as e:
        logger.error(f"Failed to send reschedule notification: {str(e)}")
        self.retry(countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_appointment_cancellation_notification(self, appointment_id: str):
    """
    Send appointment cancellation notification.
    """
    from apps.appointments.models import Appointment
    from apps.notifications.models import Notification, NotificationTemplate
    from apps.notifications.whatsapp import whatsapp_service
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        patient = appointment.patient
        
        template, _ = NotificationTemplate.objects.get_or_create(
            template_type='appointment_cancellation',
            defaults={
                'name': 'Appointment Cancelled',
                'channel': 'whatsapp',
                'body': '''❌ *Appointment Cancelled*

Dear {{patient_name}},

Your appointment has been cancelled:

👨‍⚕️ Doctor: Dr. {{doctor_name}}
📅 Date: {{date}}
⏰ Time: {{time}}

To reschedule, reply BOOK or visit our website.

We apologize for any inconvenience.''',
                'available_variables': ['patient_name', 'doctor_name', 'date', 'time']
            }
        )
        
        context = {
            'patient_name': patient.user.full_name,
            'doctor_name': appointment.doctor.user.full_name,
            'date': appointment.appointment_date.strftime('%B %d, %Y'),
            'time': appointment.start_time.strftime('%I:%M %p')
        }
        
        message = template.render(context)
        recipient_number = patient.user.whatsapp_number or patient.user.phone_number
        
        if recipient_number:
            result = whatsapp_service.send_message(recipient_number, message)
            
            Notification.objects.create(
                template=template,
                recipient=patient.user,
                channel='whatsapp',
                recipient_contact=recipient_number,
                body=message,
                appointment=appointment,
                status='sent' if result['success'] else 'failed',
                external_id=result.get('message_id', ''),
                sent_at=timezone.now() if result['success'] else None
            )
        
        logger.info(f"Cancellation notification sent for appointment: {appointment_id}")
        
    except Exception as e:
        logger.error(f"Failed to send cancellation notification: {str(e)}")
        self.retry(countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_appointment_reminder(self, appointment_id: str):
    """
    Send appointment reminder (typically 24 hours before).
    """
    from apps.appointments.models import Appointment
    from apps.notifications.models import Notification, NotificationTemplate
    from apps.notifications.whatsapp import whatsapp_service
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        if appointment.status not in ['scheduled', 'confirmed', 'rescheduled']:
            return
        
        patient = appointment.patient
        
        template, _ = NotificationTemplate.objects.get_or_create(
            template_type='appointment_reminder',
            defaults={
                'name': 'Appointment Reminder',
                'channel': 'whatsapp',
                'body': '''⏰ *Appointment Reminder*

Dear {{patient_name}},

This is a reminder for your upcoming appointment:

👨‍⚕️ Doctor: Dr. {{doctor_name}}
📅 Tomorrow: {{date}}
⏰ Time: {{time}}
🏢 Clinic: {{clinic_name}}
🎫 Token: #{{token_number}}

Please arrive 15 minutes early.
Bring any relevant medical reports.

Reply CONFIRM to confirm or CANCEL to cancel.''',
                'available_variables': [
                    'patient_name', 'doctor_name', 'date', 'time',
                    'clinic_name', 'token_number'
                ]
            }
        )
        
        context = {
            'patient_name': patient.user.full_name,
            'doctor_name': appointment.doctor.user.full_name,
            'date': appointment.appointment_date.strftime('%A, %B %d, %Y'),
            'time': appointment.start_time.strftime('%I:%M %p'),
            'clinic_name': appointment.clinic.name,
            'token_number': appointment.token_number or 'TBD'
        }
        
        message = template.render(context)
        recipient_number = patient.user.whatsapp_number or patient.user.phone_number
        
        if recipient_number:
            result = whatsapp_service.send_message(recipient_number, message)
            
            Notification.objects.create(
                template=template,
                recipient=patient.user,
                channel='whatsapp',
                recipient_contact=recipient_number,
                body=message,
                appointment=appointment,
                status='sent' if result['success'] else 'failed',
                external_id=result.get('message_id', ''),
                sent_at=timezone.now() if result['success'] else None
            )
            
            # Mark reminder as sent
            appointment.reminder_sent = True
            appointment.reminder_sent_at = timezone.now()
            appointment.save(update_fields=['reminder_sent', 'reminder_sent_at'])
        
        logger.info(f"Reminder sent for appointment: {appointment_id}")
        
    except Exception as e:
        logger.error(f"Failed to send reminder: {str(e)}")
        self.retry(countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def notify_waitlist_patients(
    self,
    doctor_id: str,
    clinic_id: str,
    date_str: str,
    time_str: str
):
    """
    Notify up to 3 waitlist patients when a slot becomes available.
    """
    from apps.patients.models import Waitlist
    from apps.notifications.models import Notification, NotificationTemplate
    from apps.notifications.whatsapp import whatsapp_service
    from datetime import datetime
    
    try:
        available_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get top 3 patients on waitlist for this doctor/clinic/date
        waitlist_entries = Waitlist.objects.filter(
            doctor_id=doctor_id,
            clinic_id=clinic_id,
            preferred_date=available_date,
            status='waiting'
        ).order_by('created_at')[:3]
        
        if not waitlist_entries:
            logger.info("No waitlist patients to notify")
            return
        
        template, _ = NotificationTemplate.objects.get_or_create(
            template_type='waitlist_notification',
            defaults={
                'name': 'Waitlist Slot Available',
                'channel': 'whatsapp',
                'body': '''🎉 *Good News! Slot Available*

Dear {{patient_name}},

A slot has opened up with Dr. {{doctor_name}} that matches your waitlist request!

📅 Date: {{date}}
⏰ Time: {{time}}
🏢 Clinic: {{clinic_name}}

Reply BOOK to confirm this slot immediately.
This offer expires in 30 minutes.

First come, first served!''',
                'available_variables': [
                    'patient_name', 'doctor_name', 'date', 'time', 'clinic_name'
                ]
            }
        )
        
        for entry in waitlist_entries:
            patient = entry.patient
            
            context = {
                'patient_name': patient.user.full_name,
                'doctor_name': entry.doctor.user.full_name,
                'date': available_date.strftime('%A, %B %d, %Y'),
                'time': time_str,
                'clinic_name': entry.clinic.name
            }
            
            message = template.render(context)
            recipient_number = patient.user.whatsapp_number or patient.user.phone_number
            
            if recipient_number:
                result = whatsapp_service.send_message(recipient_number, message)
                
                Notification.objects.create(
                    template=template,
                    recipient=patient.user,
                    channel='whatsapp',
                    recipient_contact=recipient_number,
                    body=message,
                    status='sent' if result['success'] else 'failed',
                    external_id=result.get('message_id', ''),
                    sent_at=timezone.now() if result['success'] else None
                )
                
                # Update waitlist entry
                entry.status = 'notified'
                entry.notification_sent_at = timezone.now()
                entry.save()
        
        logger.info(f"Waitlist notifications sent: {waitlist_entries.count()} patients")
        
    except Exception as e:
        logger.error(f"Failed to notify waitlist patients: {str(e)}")
        self.retry(countdown=60 * (self.request.retries + 1))


@shared_task
def send_daily_appointment_reminders():
    """
    Scheduled task to send reminders for tomorrow's appointments.
    Run daily via Celery Beat.
    """
    from apps.appointments.models import Appointment
    from datetime import date, timedelta
    
    tomorrow = date.today() + timedelta(days=1)
    
    appointments = Appointment.objects.filter(
        appointment_date=tomorrow,
        status__in=['scheduled', 'confirmed', 'rescheduled'],
        reminder_sent=False,
        is_active=True
    )
    
    for appointment in appointments:
        send_appointment_reminder.delay(str(appointment.id))
    
    logger.info(f"Queued {appointments.count()} reminder notifications")
