from django.db import models
from django.contrib.auth.models import User


class Horse(models.Model):
    """Represents a horse that can be ridden by multiple riders."""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Rider(models.Model):
    """Represents a rider who can ride multiple horses."""
    name = models.CharField(max_length=100)
    horse = models.ForeignKey(Horse, on_delete=models.CASCADE, related_name='riders')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.horse.name})"

    class Meta:
        unique_together = ('name', 'horse')
        ordering = ['horse', 'name']


class JournalEntry(models.Model):
    """Represents a journal entry created by a rider."""
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='journal_entries')
    text_content = models.TextField(blank=True)
    image = models.ImageField(upload_to='journal_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    alerted_michelle = models.BooleanField(default=False)

    def __str__(self):
        return f"Entry by {self.rider.name} on {self.created_at.date()}"

    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    """Represents a comment from Michelle (head trainer) on a journal entry."""
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.entry}"

    class Meta:
        ordering = ['created_at']


class Event(models.Model):
    """Represents a calendar event for a horse (competition, vet appointment, etc.)"""
    EVENT_TYPES = [
        ('competition', 'Competition'),
        ('vet', 'Vet Appointment'),
        ('farrier', 'Farrier Visit'),
        ('other', 'Other'),
    ]
    
    horse = models.ForeignKey(Horse, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    created_by = models.ForeignKey(Rider, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.horse.name} - {self.title} ({self.date})"

    class Meta:
        ordering = ['date', 'time']
