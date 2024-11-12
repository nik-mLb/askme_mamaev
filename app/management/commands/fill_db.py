from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Question, Answer, Tag, QuestionLike, AnswerLike, Profile
from django.utils import timezone
import random
import string

class Command(BaseCommand):
    help = 'Fills the database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help="The ratio of data to populate")

    def handle(self, *args, **options):
        ratio = options['ratio']

        self.stdout.write(f"Starting to fill the database with ratio {ratio}")


        # Создаем пользователей и тэги и профили
        self.stdout.write("Creating users and tags and profiles...")
        users = []
        tags = []
        profiles = []
        k = 0.2
        for i in range(ratio):
            if i == int(ratio * k):
                self.stdout.write(f"{int(k * 100)}% processed...")
                k += 0.2
            user = User(
                username=f'user_{i}',
                email=f'user_{i}@example.com',
                password = 'password'
            )
            profiles.append(Profile(user=user))
            users.append(user)

            tag_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))
            tags.append(Tag(name=tag_name))
        User.objects.bulk_create(users)
        users = list(User.objects.all())
        Tag.objects.bulk_create(tags)
        tags = list(Tag.objects.all())
        Profile.objects.bulk_create(profiles)
        profiles = list(Profile.objects.all())

        # Создаем вопросы
        self.stdout.write("Creating questions...")
        questions = []
        k = 0.2
        for i in range(ratio * 10):
            if i == int(ratio * 10 * k):
                self.stdout.write(f"{int(k * 100)}% processed...")
                k += 0.2
            question = Question(
                title=f"Question title {i}",
                author=random.choice(profiles),
                body="This is a sample question body.",
                created_at=timezone.now()
            )
            questions.append(question)
        Question.objects.bulk_create(questions)
        questions = list(Question.objects.all())

        # Соединяем тэги и вопросы
        self.stdout.write("connecting tags with questions...")
        for question in questions:
            question.tags.set(random.sample(tags, k=random.randint(1, 5)))
        self.stdout.write("connecting finished")

        # Создаем ответы
        self.stdout.write("Creating answers...")
        answers = []
        k = 0.2
        for i in range(ratio * 100):
            if i == int(ratio * 100 * k):
                self.stdout.write(f"{int(k * 100)}% processed...")
                k += 0.2
            answer = Answer(
                author=random.choice(profiles),
                question=random.choice(questions),
                body="This is a sample answer.",
                created_at=timezone.now()
            )
            answers.append(answer)
        Answer.objects.bulk_create(answers)
        answers = list(Answer.objects.all())

        # Создаем лайки вопросов и лайки ответов
        self.stdout.write("Creating question likes and answer likes...")
        question_likes = []
        existing_question_likes = set()
        answer_likes = []
        existing_answer_likes = set()
        k = 0.2
        for i in range(ratio * 200):
            if i == int(ratio * 200 * k):
                self.stdout.write(f"{int(k * 100)}% processed...")
                k += 0.2
            user = random.choice(profiles)
            question = random.choice(questions)
            like_question_key = (user.id, question.id)
            if like_question_key not in existing_question_likes:
                question_likes.append(QuestionLike(user=user, question=question))
                existing_question_likes.add(like_question_key)
            
            user = random.choice(profiles)
            answer = random.choice(answers)
            like_answer_key = (user.id, answer.id)
            if like_answer_key not in existing_answer_likes:
                answer_likes.append(AnswerLike(user=user, answer=answer))
                existing_answer_likes.add(like_answer_key)

        QuestionLike.objects.bulk_create(question_likes)
        AnswerLike.objects.bulk_create(answer_likes)

        self.stdout.write(self.style.SUCCESS('Successfully filled the database'))
