from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Question, Tag, Answer, QuestionLike
from .utils import paginate, get_default_context, get_question_context, get_base_context, get_tag_context

def index(request):
    page = paginate(Question.objects.new_questions(), request)
    return render(
        request, 'index.html', 
        context = get_default_context(page)
    )

def hot(request):
    page = paginate(Question.objects.best_questions(), request)
    return render(
        request, 'hot.html', 
        context = get_default_context(page)
    )

def question(request, question_id):
    question_obj = get_object_or_404(Question, id=question_id)
    page = paginate(question_obj.answers.all(), request)
    return render(
        request, 'one_question.html', 
        context = get_question_context(question_obj, page)
    )

def login(request):
    return render(
        request, 'login.html',
        context = get_base_context()
    )

def signup(request):
    return render(
        request, 'signup.html',
        context = get_base_context()
    )

def ask(request):
    return render(
        request, 'ask.html',
        context = get_base_context()
    )

def tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    page = paginate(tag.tags_question.all(), request)
    return render(
        request, 'tag.html', 
        context = get_tag_context(tag_name, page)
    )

def settings(request):
    return render(
        request, 'settings.html',
        context = get_base_context()
    )