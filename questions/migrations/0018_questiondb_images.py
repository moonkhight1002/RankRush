from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0017_merge_20210127_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question_db',
            name='question',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='question_db',
            name='optionA',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='question_db',
            name='optionB',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='question_db',
            name='optionC',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='question_db',
            name='optionD',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='question_db',
            name='question_image',
            field=models.ImageField(blank=True, null=True, upload_to='question_media'),
        ),
        migrations.AddField(
            model_name='question_db',
            name='optionA_image',
            field=models.ImageField(blank=True, null=True, upload_to='question_media'),
        ),
        migrations.AddField(
            model_name='question_db',
            name='optionB_image',
            field=models.ImageField(blank=True, null=True, upload_to='question_media'),
        ),
        migrations.AddField(
            model_name='question_db',
            name='optionC_image',
            field=models.ImageField(blank=True, null=True, upload_to='question_media'),
        ),
        migrations.AddField(
            model_name='question_db',
            name='optionD_image',
            field=models.ImageField(blank=True, null=True, upload_to='question_media'),
        ),
    ]
