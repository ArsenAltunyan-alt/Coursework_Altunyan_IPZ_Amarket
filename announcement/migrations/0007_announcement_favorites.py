from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0006_announcement_latitude_announcement_longitude'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='favorites',
            field=models.ManyToManyField(blank=True, related_name='favorite_announcements', to=settings.AUTH_USER_MODEL),
        ),
    ]
