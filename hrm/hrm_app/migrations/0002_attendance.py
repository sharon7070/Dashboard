# Generated by Django 5.2 on 2025-05-11 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrm_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('employee_id', models.CharField(max_length=20)),
                ('employee_name', models.CharField(max_length=100)),
                ('clock_in', models.TimeField()),
                ('clock_out', models.TimeField()),
                ('break_hours', models.DecimalField(decimal_places=2, max_digits=4)),
                ('total_hours', models.DecimalField(decimal_places=2, max_digits=5)),
                ('status', models.CharField(max_length=20)),
            ],
        ),
    ]
