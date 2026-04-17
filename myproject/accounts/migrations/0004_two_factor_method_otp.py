from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_add_two_factor_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='two_factor_method',
            field=models.CharField(
                blank=True,
                choices=[('email', 'Email OTP'), ('app', 'Google Authenticator')],
                default='email',
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='two_factor_otp',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='two_factor_otp_expiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
