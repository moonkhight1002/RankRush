from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0004_activeexamsession'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProctoringSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idle_baseline', models.FloatField(default=0.018)),
                ('speech_threshold', models.FloatField(default=0.12)),
                ('ambient_threshold', models.FloatField(default=0.17)),
                ('voice_match_threshold', models.FloatField(default=0.58)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Proctoring Settings',
                'verbose_name_plural': 'Proctoring Settings',
            },
        ),
    ]
