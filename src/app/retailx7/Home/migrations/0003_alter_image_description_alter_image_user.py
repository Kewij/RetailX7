# Generated by Django 4.2 on 2024-11-23 17:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0002_alter_image_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_images', to=settings.AUTH_USER_MODEL),
        ),
    ]