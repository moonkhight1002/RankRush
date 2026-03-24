from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0005_proctoringsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='proctoringsettings',
            name='gaze_away_ms',
            field=models.IntegerField(default=2500),
        ),
        migrations.AddField(
            model_name='proctoringsettings',
            name='multi_face_ms',
            field=models.IntegerField(default=1500),
        ),
        migrations.AddField(
            model_name='proctoringsettings',
            name='no_face_ms',
            field=models.IntegerField(default=2500),
        ),
        migrations.AddField(
            model_name='proctoringsettings',
            name='precheck_ms',
            field=models.IntegerField(default=1500),
        ),
    ]
