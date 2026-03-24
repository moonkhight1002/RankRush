from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0006_proctoringtimings'),
    ]

    operations = [
        migrations.AddField(
            model_name='proctoringsettings',
            name='ambient_range_summary',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='proctoringsettings',
            name='quiet_range_summary',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='proctoringsettings',
            name='speech_range_summary',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
