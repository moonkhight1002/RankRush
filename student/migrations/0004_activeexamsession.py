from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0017_merge_20210127_1143'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('student', '0003_examviolationlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveExamSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exam_id', models.IntegerField()),
                ('exam_name', models.CharField(max_length=100)),
                ('session_token', models.CharField(max_length=64, unique=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('stale', 'Stale')], default='active', max_length=12)),
                ('started_at', models.DateTimeField(default=timezone.now)),
                ('last_seen_at', models.DateTimeField(default=timezone.now)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('professor', models.ForeignKey(blank=True, limit_choices_to={'groups__name': 'Professor'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='active_exam_sessions', to=settings.AUTH_USER_MODEL)),
                ('qpaper', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='questions.question_paper')),
                ('student', models.ForeignKey(limit_choices_to={'groups__name': 'Student'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Active Exam Session',
                'verbose_name_plural': 'Active Exam Sessions',
                'ordering': ['-last_seen_at'],
            },
        ),
    ]
