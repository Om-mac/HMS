"""
Base models for HMS application.
"""
import uuid
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model with created and modified timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract base model with UUID primary key.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel):
    """
    Abstract base model combining UUID and timestamps.
    """
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        """Soft delete the record."""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
    
    def restore(self):
        """Restore a soft-deleted record."""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])


class ActiveManager(models.Manager):
    """
    Manager that returns only active records.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SoftDeleteModel(BaseModel):
    """
    Abstract model with soft delete functionality and active manager.
    """
    objects = models.Manager()  # Default manager
    active = ActiveManager()  # Only active records
    
    class Meta:
        abstract = True
