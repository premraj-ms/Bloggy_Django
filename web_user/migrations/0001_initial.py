# Generated by Django 5.1.3 on 2024-12-23 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post_image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.ImageField(upload_to='Post_Images')),
                ('image_by', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Web_post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_title', models.CharField(blank=True, default='untitled', max_length=80)),
                ('post_author', models.IntegerField()),
                ('post_category', models.IntegerField()),
                ('post_desc', models.CharField(blank=True, max_length=160, null=True)),
                ('post_cover', models.ImageField(upload_to='Post_cover')),
                ('post_content', models.TextField()),
                ('post_published', models.BooleanField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('view_count', models.IntegerField(default=0)),
                ('post_slug', models.SlugField(max_length=100, unique=True)),
                ('ghjk', models.SlugField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Web_users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.SlugField(max_length=100, unique=True)),
                ('full_name', models.CharField(max_length=60)),
                ('user_email', models.EmailField(max_length=260, unique=True)),
                ('user_bio', models.CharField(blank=True, max_length=190, null=True)),
                ('user_profile_image', models.ImageField(default='user_Profile_image/default.png', upload_to='user_Profile_image')),
                ('user_about', models.CharField(blank=True, max_length=500, null=True)),
                ('user_skills', models.CharField(blank=True, max_length=300, null=True)),
                ('user_password', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('verified', models.BooleanField(default=False)),
            ],
        ),
    ]
