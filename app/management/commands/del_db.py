from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Question, Answer, Tag, QuestionLike, AnswerLike, Profile

class Command(BaseCommand):
    help = 'Fills the database with test data'
    def handle(self, *args, **options):
        self.stdout.write("Cleaning up old data...")
        User.objects.filter(username__startswith='user_').delete()
        Tag.objects.all().delete()
        Question.objects.all().delete()
        Answer.objects.all().delete()
        QuestionLike.objects.all().delete()
        AnswerLike.objects.all().delete()
        Profile.objects.all().delete()