from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0017_merge_20210127_1143'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('student', '0002_stu_question_stuexam_db_sturesults_db'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamViolationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exam_id', models.IntegerField(blank=True, null=True)),
                ('exam_name', models.CharField(max_length=100)),
                ('violation_type', models.CharField(max_length=50)),
                ('detail', models.CharField(blank=True, max_length=255)),
                ('violation_count', models.IntegerField(default=1)),
                ('session_token', models.CharField(blank=True, max_length=64)),
                ('created_at', models.DateTimeField(default=timezone.now)),
                ('professor', models.ForeignKey(blank=True, limit_choices_to={'groups__name': 'Professor'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exam_violation_logs', to=settings.AUTH_USER_MODEL)),
                ('qpaper', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='questions.question_paper')),
                ('student', models.ForeignKey(limit_choices_to={'groups__name': 'Student'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Exam Violation Log',
                'verbose_name_plural': 'Exam Violation Logs',
                'ordering': ['-created_at'],
            },
        ),
    ]
