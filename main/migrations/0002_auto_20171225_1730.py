# Generated by Django 2.0 on 2017-12-25 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mosaicpicture',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='mosaic_pictures', to='main.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='mosaicsite',
            name='archeological_context',
            field=models.CharField(blank=True, choices=[('church', 'Church'), ('synagogue', 'Synagogue'), ('public', 'Public building')], max_length=50, verbose_name='Archeological context'),
        ),
        migrations.AddField(
            model_name='mosaicsite',
            name='featured',
            field=models.BooleanField(default=False, verbose_name='Is featured?'),
        ),
        migrations.AddField(
            model_name='mosaicsite',
            name='latitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Latitude'),
        ),
        migrations.AddField(
            model_name='mosaicsite',
            name='longitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Longitude'),
        ),
    ]