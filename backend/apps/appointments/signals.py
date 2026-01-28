"""
Django signals for appointment status changes.
Triggers WhatsApp notifications via Celery tasks.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Appointment, AppointmentHistory
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Appointment)
def track_status_change(sender, instance, **kwargs):
    """Track status changes before saving."""
    if instance.pk:
        try:
            old_instance = Appointment.objects.get(pk=instance.pk)
            instance._previous_status = old_instance.status
            instance._status_changed = old_instance.status != instance.status
            instance._previous_date = old_instance.appointment_date
            instance._previous_time = old_instance.start_time
        except Appointment.DoesNotExist:
            instance._status_changed = False
    else:
        instance._status_changed = False


@receiver(post_save, sender=Appointment)
def handle_appointment_status_change(sender, instance, created, **kwargs):
    """
    Handle appointment status changes:
    - Create history entry
    - Trigger WhatsApp notifications
    - Handle waitlist for cancelled slots
    """
    from apps.notifications.tasks import (
        send_appointment_confirmation,
        send_appointment_reschedule_notification,
        send_appointment_cancellation_notification,
        send_appointment_reminder,
        notify_waitlist_patients
    )
    
    # New appointment created
    if created:
        logger.info(f"New appointment created: {instance.id}")
        # Send confirmation notification
        send_appointment_confirmation.delay(str(instance.id))
        return
    
    # Status changed
    if hasattr(instance, '_status_changed') and instance._status_changed:
        previous_status = getattr(instance, '_previous_status', 'unknown')
        
        # Create history entry
        AppointmentHistory.objects.create(
            appointment=instance,
            previous_status=previous_status,
            new_status=instance.status,
            changed_by=getattr(instance, '_changed_by', None)
        )
        
        logger.info(f"Appointment {instance.id} status changed: {previous_status} -> {instance.status}")
        
        # Handle rescheduled appointments
        if instance.status == 'rescheduled':
            send_appointment_reschedule_notification.delay(str(instance.id))
        
        # Handle cancelled appointments - trigger waitlist
        elif instance.status == 'cancelled':
            send_appointment_cancellation_notification.delay(str(instance.id))
            
            # Notify waitlist patients about the freed slot
            notify_waitlist_patients.delay(
                str(instance.doctor_id),
                str(instance.clinic_id),
                str(instance.appointment_date),
                str(instance.start_time)
            )
        
        # Handle check-in
        elif instance.status == 'checked_in':
            from django.utils import timezone
            if not instance.checked_in_at:
                instance.checked_in_at = timezone.now()
                instance.save(update_fields=['checked_in_at'])
        
        # Handle completion
        elif instance.status == 'completed':
            logger.info(f"Appointment {instance.id} completed")


@receiver(post_save, sender=Appointment)
def handle_appointment_reschedule(sender, instance, created, **kwargs):
    """
    Handle date/time changes (rescheduling).
    """
    if created:
        return
    
    from apps.notifications.tasks import send_appointment_reschedule_notification
    
    # Check if date or time changed
    previous_date = getattr(instance, '_previous_date', None)
    previous_time = getattr(instance, '_previous_time', None)
    
    date_changed = previous_date and previous_date != instance.appointment_date
    time_changed = previous_time and previous_time != instance.start_time
    
    if date_changed or time_changed:
        # Store original date/time if not already stored
        if not instance.original_date:
            instance.original_date = previous_date
            instance.original_time = previous_time
            instance.save(update_fields=['original_date', 'original_time'])
        
        logger.info(f"Appointment {instance.id} rescheduled from {previous_date} {previous_time}")
        send_appointment_reschedule_notification.delay(str(instance.id))
