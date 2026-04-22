from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentPreferences', '0003_authidentifiersettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='authidentifiersettings',
            name='username_mode',
            field=models.CharField(
                choices=[
                    ('manual', 'Manual username entry'),
                    ('email_prefix', 'Use the email prefix as username'),
                ],
                default='manual',
                max_length=20,
                verbose_name='Username mode',
            ),
        ),
    ]
