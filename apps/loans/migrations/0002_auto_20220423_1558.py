# Generated by Django 3.2.13 on 2022-04-23 15:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('loans', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='loanterm',
            options={'verbose_name': 'Loan Term', 'verbose_name_plural': 'Loan Terms'},
        ),
        migrations.RemoveField(
            model_name='loanterm',
            name='payment_date',
        ),
        migrations.AddField(
            model_name='loanterm',
            name='paid_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='paid date'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approved_by', to=settings.AUTH_USER_MODEL, verbose_name='approved by'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='approved_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='approved date'),
        ),
        migrations.AlterField(
            model_name='loanterm',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='due date'),
        ),
    ]
