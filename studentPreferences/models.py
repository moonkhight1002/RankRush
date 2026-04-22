from django.db import models
from django.contrib.auth.models import User


class AuthIdentifierSettings(models.Model):
    MODE_MANUAL = 'manual'
    MODE_EMAIL_PREFIX = 'email_prefix'
    POSITION_PREFIX = 'prefix'
    POSITION_SUFFIX = 'suffix'

    MODE_CHOICES = [
        (MODE_MANUAL, 'Manual username entry'),
        (MODE_EMAIL_PREFIX, 'Use the email prefix as username'),
    ]

    POSITION_CHOICES = [
        (POSITION_PREFIX, 'Before the username'),
        (POSITION_SUFFIX, 'After the username'),
    ]

    username_mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default=MODE_MANUAL,
        verbose_name='Username mode',
    )
    username_affix = models.CharField(
        max_length=80,
        blank=True,
        default='',
        verbose_name='Institute username text',
        help_text='Optional text to attach automatically, for example @xyz.ac.in or college-.',
    )
    affix_position = models.CharField(
        max_length=10,
        choices=POSITION_CHOICES,
        default=POSITION_SUFFIX,
        verbose_name='Text position',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Institute Username Settings'
        verbose_name_plural = 'Institute Username Settings'

    def __str__(self):
        affix = (self.username_affix or '').strip()
        if not affix:
            return 'Default username login'
        placement = 'before' if self.affix_position == self.POSITION_PREFIX else 'after'
        return f'Username affix {placement}: {affix}'

    def save(self, *args, **kwargs):
        self.pk = 1
        self.username_affix = (self.username_affix or '').strip()
        return super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'username_mode': cls.MODE_MANUAL,
                'username_affix': '',
                'affix_position': cls.POSITION_SUFFIX,
            }
        )
        return obj


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
