from django.db import models
from django.contrib.auth.models import User

class StudentPreferenceModel(models.Model): 
    user = models.OneToOneField(to = User,on_delete=models.CASCADE)
    sendEmailOnLogin = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user) + 's' + 'preferences' 


class SupportTicket(models.Model):
    TYPE_FEEDBACK = 'feedback'
    TYPE_ISSUE = 'issue'
    TYPE_HELP = 'help'
    TYPE_EMAIL_CHANGE = 'email_change'

    TYPE_CHOICES = [
        (TYPE_FEEDBACK, 'Feedback'),
        (TYPE_ISSUE, 'Issue Report'),
        (TYPE_HELP, 'Help Request'),
        (TYPE_EMAIL_CHANGE, 'Email Change Request'),
    ]

    ROLE_STUDENT = 'student'
    ROLE_FACULTY = 'faculty'

    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_FACULTY, 'Faculty'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    registered_email = models.EmailField()
    ticket_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_HELP)
    subject = models.CharField(max_length=120)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'

    def __str__(self):
        return f"{self.get_role_display()} - {self.user.username} - {self.subject}"
