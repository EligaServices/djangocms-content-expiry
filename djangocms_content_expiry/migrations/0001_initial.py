# Generated by Django 2.2.24 on 2021-07-13 08:58

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContentExpiry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ContentExpiryContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Page', 'Page'), ('Alias', 'Alias')], max_length=50)),
                ('from_expiry_date', models.DateField(default=datetime.date.today, verbose_name='From Expiry Date')),
                ('to_expiry_date', models.DateField(default=datetime.date.today, verbose_name='To Expiry Date')),
                ('page_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djangocms_content_expiry.ContentExpiry')),
            ],
            options={
                'verbose_name': 'Content Expiry',
            },
        ),
    ]
