from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from django.urls import reverse

class ProfileManager(models.Manager):
    def get_popular_users(self):
        return self.annotate(
            question_count=Count('author_question'),
            answer_count=Count('author_answer')
        ).order_by('-question_count', '-answer_count')[:5]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="uploads/", null=True, blank=True)

    objects = ProfileManager()
    def __str__(self):
        return self.user.username


class TagManager(models.Manager):
    def get_popular(self):
        return self.annotate(num_questions=Count('tags_question')).order_by('-num_questions')[:9]
    
class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    objects = TagManager()
    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def best_questions(self):
        return self.annotate(like_count=models.Count("likes_question")).order_by("-like_count")

    def new_questions(self):
        return self.order_by("-created_at")
    


class Question(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="author_question")
    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="tags_question")

    def get_absolute_url(self):
        return reverse("one_question", args=[str(self.id)])
    
    def like_count(self):
        return self.likes_question.count()
    
    def answer_count(self):
        return self.answers.count()

    objects = QuestionManager()

    def __str__(self):
        return self.title


class Answer(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="author_answer")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return f"Answer to: {self.question.title}"


class QuestionLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="question_likes")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="likes_question")

    class Meta:
        unique_together = ("user", "question")

    def __str__(self):
        return f"{self.user.user.username} likes {self.question.title}"


class AnswerLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="answer_likes")
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ("user", "answer")

    def __str__(self):
        return f"{self.user.user.username} likes answer to {self.answer.question.title}"
