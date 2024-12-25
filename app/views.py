import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Tag, Answer, QuestionLike, Profile
from .utils import (paginate, get_default_context, get_question_context, get_ask_context, 
    get_tag_context, get_login_context, get_signup_context, get_settings_context, get_like_question_context,
    get_like_question_context_async, get_like_answer_context_async, get_correct_answer_context )
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, SearchHeadline
from django.contrib import auth
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

def index(request):
    page = paginate(Question.objects.new_questions(), request)
    return render(
        request, 'index.html', 
        context = get_default_context(request, page)
    )

def hot(request):
    page = paginate(Question.objects.best_questions(), request)
    return render(
        request, 'hot.html', 
        context = get_default_context(request, page)
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
        context = get_tag_context(request, tag_name, page)
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

@login_required
def like_question(request, question_id):
    url = get_like_question_context(request, question_id)
    return redirect(url)

@require_POST
@login_required
def like_question_async(request, question_id):
    return get_like_question_context_async(request, question_id)

@require_POST
@login_required
def like_answer_async(request, question_id, answer_id):
    return get_like_answer_context_async(request, question_id, answer_id)

@require_POST
@login_required
def set_correct_answer(request, question_id, answer_id):
    return get_correct_answer_context(request, question_id, answer_id)

def search_questions(request):
    query = request.GET.get('q', '')
    if query:
        search_query = SearchQuery(query)
        search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
        results = Question.objects.annotate(
            rank=SearchRank(search_vector, search_query),
            headline_title=SearchHeadline('title', search_query),
            headline_body=SearchHeadline('body', search_query)
        ).filter(rank__gte=0.1).order_by('-rank')[:10]  # Ограничиваем результаты до 10
    else:
        results = []

    return render(request, 'search_results.html', {'results': results})