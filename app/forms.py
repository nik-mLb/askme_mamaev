from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, Question, Tag, Answer

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        return self.cleaned_data['username'].lower().strip()
    
class RegisterForm(forms.ModelForm):
    email = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput, label="Repeat Password")
    avatar = forms.ImageField(required=False, label="Upload Avatar")

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if email:
            email = email.strip()
            if User.objects.filter(email=email).exists():
                self.add_error('email', "This email is already in use.")
        if password and password_confirmation and password != password_confirmation:
            self.add_error('password_confirmation', "Passwords do not match.")

        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
            profile = Profile(user=user, avatar=self.cleaned_data.get("avatar"))
            profile.save()

        return user
    
class SettinsForm(forms.ModelForm):
    avatar = forms.ImageField(required=False, label="Upload Avatar")

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)
        if self.profile:
            self.fields['avatar'].initial = self.profile.avatar

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        username = cleaned_data.get("username")

        if username:
            username = username.strip() if username else None
            if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                self.add_error('username', "This username is already in use.")

        if not email:
            self.add_error('email', "Email is required.")
        else:
            if User.objects.filter(email=email.strip()).exclude(pk=self.instance.pk).exists():
                self.add_error('email', "This email is already in use.")

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if self.profile:
                self.profile.avatar = self.cleaned_data.get('avatar', self.profile.avatar)
                self.profile.save()
        return user
    
class AskForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea, required=True, label="Text")
    tags = forms.CharField(required=False) 

    class Meta:
        model = Question
        fields = ('title', 'body', 'tags')

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        tags = cleaned_data.get("tags")

        if title:
            if Question.objects.filter(title = title.strip()).exclude(pk=self.instance.pk).exists():
                self.add_error('title', "This title is already in use.")
            if len(title) < 3:
                self.add_error('title', "Too short title (min 3)")

        if tags:
            tag_list = [tag.strip() for tag in tags.split()]
            if len(tag_list) > 3:
                self.add_error('tags', "You can only add up to 3 tags.")
        
        return cleaned_data

    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        if author:
            question.author = author
        if commit:
            question.save()
        
        tagss = self.cleaned_data['tags']
        if tagss:
            tag_list = [tag.strip() for tag in tagss.split()]
            for tag_name in tag_list:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)  # Теперь можно добавлять теги

        return question


class AnswerForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea,  label="Text")

    class Meta:
        model = Answer
        fields = ('body',)


        

    def save(self, commit=True):
        answer = super().save(commit=False)
        if commit:
            answer.save()

        return answer