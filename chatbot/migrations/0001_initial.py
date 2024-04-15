# Generated by Django 4.1 on 2024-04-15 18:08

import chatbot.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('name', 'user')},
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('file', models.FileField(upload_to=chatbot.models.create_file_path)),
                ('isVerified', models.BooleanField(default=False)),
                ('embeddingStatus', models.CharField(choices=[('COMPLETED', 'COMPLETED'), ('PENDING', 'PENDING'), ('NOT APPROVED', 'NOT APPROVED'), ('PROCESSING', 'PROCESSING')], default='NOT APPROVED', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='QueryFeedBack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('rating', models.PositiveSmallIntegerField()),
                ('feedback', models.TextField(blank=True)),
                ('expected_response', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=256)),
                ('response', models.TextField()),
                ('time', models.DateTimeField()),
                ('context', models.TextField()),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='queries', to='chatbot.chat')),
                ('doc_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='queries', to='chatbot.document')),
            ],
        ),
    ]
