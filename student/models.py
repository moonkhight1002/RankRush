from django.db import models
from django.contrib.auth.models import User
from questions.question_models import Question_DB
from questions.questionpaper_models import Question_Paper
from django.utils import timezone

class StudentInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, blank=True)
    stream = models.CharField(max_length=50, blank=True)
    picture = models.ImageField(upload_to = 'student_profile_pics', blank=True)

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name_plural = 'Student Info'

class Stu_Question(Question_DB):
    professor = None
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE, null=True)
    choice = models.CharField(max_length=3, default="E")

    def __str__(self):
        return str(self.student.username) + " "+ str(self.qno) +"-Stu_QuestionDB"


class StuExam_DB(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE, null=True)
    examname = models.CharField(max_length=100)
    qpaper = models.ForeignKey(Question_Paper, on_delete=models.CASCADE, null=True)
    questions = models.ManyToManyField(Stu_Question)
    score = models.IntegerField(default=0)
    completed = models.IntegerField(default=0)

    def __str__(self):
        return str(self.student.username) +" " + str(self.examname) + " " + str(self.qpaper.qPaperTitle) + "-StuExam_DB"


class StuResults_DB(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE, null=True)
    exams = models.ManyToManyField(StuExam_DB)

    def __str__(self):
        return str(self.student.username) +" -StuResults_DB"


class ExamViolationLog(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE)
    professor = models.ForeignKey(
        User,
        limit_choices_to={'groups__name': "Professor"},
        on_delete=models.CASCADE,
        related_name='exam_violation_logs',
        null=True,
        blank=True,
    )
    exam_id = models.IntegerField(null=True, blank=True)
    exam_name = models.CharField(max_length=100)
    qpaper = models.ForeignKey(Question_Paper, on_delete=models.CASCADE, null=True, blank=True)
    violation_type = models.CharField(max_length=50)
    detail = models.CharField(max_length=255, blank=True)
    violation_count = models.IntegerField(default=1)
    session_token = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Exam Violation Log'
        verbose_name_plural = 'Exam Violation Logs'

    def __str__(self):
        return f"{self.student.username} - {self.exam_name} - {self.violation_type}"


class ActiveExamSession(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_STALE = 'stale'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_STALE, 'Stale'),
    ]

    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE)
    professor = models.ForeignKey(
        User,
        limit_choices_to={'groups__name': "Professor"},
        on_delete=models.CASCADE,
        related_name='active_exam_sessions',
        null=True,
        blank=True,
    )
    exam_id = models.IntegerField()
    exam_name = models.CharField(max_length=100)
    qpaper = models.ForeignKey(Question_Paper, on_delete=models.CASCADE, null=True, blank=True)
    session_token = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    started_at = models.DateTimeField(default=timezone.now)
    last_seen_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-last_seen_at']
        verbose_name = 'Active Exam Session'
        verbose_name_plural = 'Active Exam Sessions'

    def __str__(self):
        return f"{self.student.username} - {self.exam_name} - {self.status}"


class ProctoringSettings(models.Model):
    idle_baseline = models.FloatField(default=0.018)
    speech_threshold = models.FloatField(default=0.12)
    ambient_threshold = models.FloatField(default=0.17)
    voice_match_threshold = models.FloatField(default=0.58)
    quiet_range_summary = models.CharField(max_length=255, blank=True, default="")
    ambient_range_summary = models.CharField(max_length=255, blank=True, default="")
    speech_range_summary = models.CharField(max_length=255, blank=True, default="")
    precheck_ms = models.IntegerField(default=1500)
    no_face_ms = models.IntegerField(default=2500)
    multi_face_ms = models.IntegerField(default=1500)
    gaze_away_ms = models.IntegerField(default=2500)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Proctoring Settings'
        verbose_name_plural = 'Proctoring Settings'

    def __str__(self):
        return "Global Proctoring Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        return super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
                defaults={
                    'idle_baseline': 0.018,
                    'speech_threshold': 0.12,
                    'ambient_threshold': 0.17,
                    'voice_match_threshold': 0.58,
                    'quiet_range_summary': '',
                    'ambient_range_summary': '',
                    'speech_range_summary': '',
                    'precheck_ms': 1500,
                    'no_face_ms': 2500,
                    'multi_face_ms': 1500,
                    'gaze_away_ms': 2500,
                }
        )
        return obj
