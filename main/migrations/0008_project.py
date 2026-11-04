import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_skill_starred_by'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('tech_stack', models.CharField(max_length=255)),
                ('project_url', models.URLField(blank=True)),
                ('project_image_url', models.URLField(blank=True)),
                ('starred_by', models.ManyToManyField(blank=True, related_name='starred_projects', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
