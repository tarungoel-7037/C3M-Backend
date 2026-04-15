from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_add_audit_obj_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterscontractroletype',
            name='group_entity_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
