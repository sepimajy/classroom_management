# Generated by Django 5.1.3 on 2024-11-26 19:43

import django.core.validators
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_remove_exam_created_at_examsubmission_feedback_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='classroom',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='submission',
            name='feedback',
        ),
        migrations.RemoveField(
            model_name='submission',
            name='grade',
        ),
        migrations.AlterField(
            model_name='assignment',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='assignments/'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='code',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='description',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='classroom',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='examsubmission',
            name='score',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='message',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='messages/'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='link',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='avatars/default.jpg', upload_to='avatars/'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('teacher', 'Teacher'), ('student', 'Student')], default='student', max_length=10),
        ),
        migrations.AlterField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='questions/'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='submissions/'),
        ),
    ]
