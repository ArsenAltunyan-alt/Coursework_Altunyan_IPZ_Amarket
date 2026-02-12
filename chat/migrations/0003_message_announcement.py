from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("announcement", "0002_category_parent"),
        ("chat", "0002_message_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="announcement",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="chat_messages",
                to="announcement.announcement",
            ),
        ),
    ]
