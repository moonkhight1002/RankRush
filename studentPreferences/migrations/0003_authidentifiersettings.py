from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentPreferences', '0002_supportticket'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthIdentifierSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username_affix', models.CharField(blank=True, default='', help_text='Optional institute text to auto-attach to usernames, for example @xyz.ac.in.', max_length=80)),
                ('affix_position', models.CharField(choices=[('prefix', 'Before username'), ('suffix', 'After username')], default='suffix', max_length=10)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Auth Identifier Settings',
                'verbose_name_plural': 'Auth Identifier Settings',
            },
        ),
    ]
