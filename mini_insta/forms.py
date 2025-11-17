# File: forms.py
# Author: Anna LaPrade (alaprade@bu.edu), 09/30/2025
# Description: forms for the mini_insta app

from django import forms
from .models import *


# allows users to create a Profile
class CreateProfileForm(forms.ModelForm):
    """Form for creating a new Profile linked to a User."""
    class Meta:
        model = Profile
        fields = ['display_name', 'bio_text', 'profile_image_url']


# allows users to create a Post 
class CreatePostForm(forms.ModelForm):
    '''A form to add an Post to the database'''

    # allows us to associate inputted caption data with a Post
    class Meta:
        '''associate this form with a model from our database'''
        model = Post
        fields = ['caption']


# allows users to create a Post 
class UpdateProfileForm(forms.ModelForm):
    '''A form to handle an update to a Profile'''

    class Meta:
        '''associates this form with a model in our database'''
        model = Profile
        fields = ['display_name', 'profile_image_url', 'bio_text'] # feilds we can update

# allows users to update a Post
class UpdatePostForm(forms.ModelForm):
    '''A form to handle an update to a Post'''

    class Meta:
        '''associates this form with a model in our database'''
        model = Post
        fields = ['caption'] # feilds we can update


# allows users to comment on a post
class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add a comment...'}),
        }