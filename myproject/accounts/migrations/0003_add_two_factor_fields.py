from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_organisation_law_firm'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='two_factor_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='two_factor_secret',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
