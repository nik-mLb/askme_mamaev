from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Tag, Answer, QuestionLike, Profile
from .utils import (paginate, get_default_context, get_question_context, get_ask_context, 
    get_tag_context, get_login_context, get_signup_context, get_settings_context)
from .forms import AnswerForm
from django.contrib import auth
from django.urls import reverse
from django.contrib.auth.decorators import login_required

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
    context = get_question_context(request, question_id)
    if isinstance(context, str):
        return redirect(context)
    return render(request, 'one_question.html', context)

def login(request):
    context = get_login_context(request)
    if isinstance(context, str):
        return redirect(context)
    return render(request, 'login.html', context)

def signup(request):
    context = get_signup_context(request)
    if isinstance(context, str):
        return redirect(context)
    return render(request, 'signup.html', context)

@login_required
def ask(request):
    context = get_ask_context(request)
    if isinstance(context, str):
        return redirect(context)
    return render(request, 'ask.html', context)

def tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    page = paginate(tag.tags_question.all(), request)
    return render(
        request, 'tag.html', 
        context = get_tag_context(tag_name, page)
    )

@login_required
def settings(request):
    context = get_settings_context(request)
    if isinstance(context, str):
        return redirect(context)
    return render(request, 'settings.html', context)

def logout(request):
    next_page = request.GET.get('next', reverse('login'))
    auth.logout(request)
    return redirect(next_page)