from django.core.management.base import BaseCommand
from django.core.cache import cache
from app.models import Tag, Profile

class Command(BaseCommand):
    help = 'Update cache for popular tags and best members'

    def handle(self, *args, **kwargs):
        # Обновляем популярные теги
        popular_tags = Tag.objects.get_popular()
        cache.set('popular_tags', popular_tags, 3600)  # Кэшируем на 1 час

        # Обновляем лучших пользователей
        members = Profile.objects.get_popular_users()
        cache.set('members', members, 3600)  # Кэшируем на 1 час

        self.stdout.write(self.style.SUCCESS('Cache updated successfully'))