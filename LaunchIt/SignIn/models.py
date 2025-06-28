from django.db import models

# Create your models here.

class VisitReason(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class IndividualSignIn(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    reason = models.ForeignKey(VisitReason, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.date}"

class EventSignIn(models.Model):
    organizer_name = models.CharField(max_length=100)
    date = models.DateField()
    reason = models.ForeignKey(VisitReason, on_delete=models.CASCADE)
    attendee_count = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.organizer_name} - {self.date} ({self.attendee_count} attendees)"
