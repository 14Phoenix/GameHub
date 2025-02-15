# Author: Mihajlo Blagojevic 0283/2021
# Author: Viktor Mitrovic 0296/2021
# Author: Tadija Goljic 0272/2021

from django.db.models import BinaryField
from django.forms import CharField, FileField, ImageField
from django import forms
from GameHubApp.models import Post, Comment


class ForumCreateForm(forms.Form):
    forum_name = CharField(label="forum_name", required=False,
                     widget=forms.TextInput(attrs={'class': 'form-control',
                                                   'placeholder': 'Enter a forum name',
                                                   'id': 'forum_name'}))
    cover_image = FileField(label="cover_image", required=False,
                     widget=forms.ClearableFileInput(attrs={'class': 'form-control',
                                                            'id': 'cover_image'}))
    banner_image = FileField(label="banner_image", required=False,
                     widget=forms.ClearableFileInput(attrs={'class': 'form-control',
                                                            'id': 'banner_image'}))
    description = CharField(label="description", required=False,
                     widget=forms.TextInput(attrs={'class': 'form-control',
                                                   'placeholder': 'Enter a description',
                                                   'id': 'banner_image'}))
    possible_number_of_players = CharField(label="possible_number_of_players", max_length=50, required=False,
                    widget=forms.TextInput(attrs={'class': 'form-control',
                                                  'placeholder': 'Enter possible number of players(ex: 1,3,5)',
                                                  'id': 'possible_number_of_players'}))


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']


class ProfileForm(forms.Form):
    profile_picture = FileField(required=False)
    profile_about_section = forms.CharField(required=False, max_length=200)
