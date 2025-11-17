# File: views.py
# Author: Anna LaPrade (alaprade@bu.edu), 09/23/2025
# Description: the view functions for the pages of the mini_insta app

from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView
from.models import *
from .forms import *
import random
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin ## for authentication
from django.contrib.auth.forms import UserCreationForm # for new Users
from django.contrib.auth.models import User # the Django user model 
from django.contrib.auth import login
# helps me handle when there is no object 
from django.shortcuts import get_object_or_404


# Create your views here.

# ShowAllView - a view to display all of the mini_insta profile
class ShowAllView(ListView):
    '''Deine a view class to show all mini_insta profiles'''

    # model type
    model = Profile

    # html template
    template_name = "mini_insta/show_all_profiles.html"

    # context
    context_object_name = "profiles"


# ProfileDetailView - a view to display one profile with all details 
class ProfileDetailView(DetailView):
    '''display a single article'''

    # model type
    model = Profile

    # html template
    template_name = "mini_insta/show_profile.html"

    # context
    context_object_name = "profile" 

    # changed this up to faciliate the logged in profile/whether or not they're following the profile they're viewing 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                # logged in suer as a varible + are they follwoing the profile they're viewing
                logged_in_profile = Profile.objects.filter(user=self.request.user).first()
                context['logged_in_profile'] = logged_in_profile
                context['is_following'] = Follower.objects.filter(
                    profile=self.object,
                    follower_profile=logged_in_profile
                ).exists()
            except Profile.DoesNotExist:
                # Admin user doesn't have a Profile
                context['logged_in_profile'] = None
                context['is_following'] = False
        else:
            # guest user stuff 
            context['logged_in_profile'] = None
            context['is_following'] = False

        return context


# PostDetailView - a view to display one post with all details 
class PostDetailView(DetailView):
    '''A view to show the details of a single Post'''

    # model type
    model = Post

    # html template
    template_name = "mini_insta/show_post.html"

    # context
    context_object_name = "post" 

    # get context data for template use
    def get_context_data(self, **kwargs):
        '''return the dicitionary of context varaibles for use in the template'''

        # calling the superclass method
        context = super().get_context_data(**kwargs)

        context['comment_form'] = CreateCommentForm()
    
        # add the profile into the context dictionary 
        if self.request.user.is_authenticated:
            profile = Profile.objects.filter(user=self.request.user).first()
            context['profile'] = profile
        else:
            context['profile'] = None

        # logged in suer as a varible + did they like the post they're viewing 
        if self.request.user.is_authenticated:
            logged_in_profile = Profile.objects.filter(user=self.request.user).first()
            context['logged_in_profile'] = logged_in_profile

            # true if this user already liked the post
            context['has_liked'] = Like.objects.filter(
                post=self.object,
                profile=logged_in_profile
            ).exists()
        else:
            # guest info
            context['logged_in_profile'] = None
            context['has_liked'] = False

        return context
    
# update view for Profiles
class UpdateProfileView(LoginRequiredMixin, UpdateView):
    '''View class to handle update of an article based on its PK.'''

    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_insta/update_profile_form.html"

    def get_object(self, queryset=None):
        # fetch the profile of the logged-in user
        return get_object_or_404(Profile, user=self.request.user)

    def get_login_url(self):
        '''return the UR for this app's login page'''

        return reverse('login')

    # create a URL to redirect users to after updating
    def get_success_url(self):
        '''Return the URL to redirect to after a sucessful update'''

        # find the PK for this profile
        pk = self.kwargs['pk']

        return reverse('show_profile', kwargs={'pk':pk})
    


class CreateProfileView(CreateView):
    '''View to create a new Profile associated with a logged-in User.
     
    Handles creation of both a User and their associated Profile.'''

    template_name = "mini_insta/create_profile_form.html"

    def get(self, request):
        user_form = UserCreationForm()
        profile_form = CreateProfileForm()
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })


    # custom to allow the 2-in-1 form
    def post(self, request):
        user_form = UserCreationForm(request.POST)
        profile_form = CreateProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            # Save the User
            user = user_form.save()

            # allows creating profile and user at same time
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.username = user.username  # set profile username same as user's
            profile.save()

            # auto-logs them in on account creation :D
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # apparenty this is faster than just get_success_url? and works better for the post method
            return redirect(reverse('show_profile', kwargs={'pk': profile.pk}))

        # if invalid, redisplay forms with errors # idk how well this works 
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })

# CreatePostView - allows post to be created
class CreatePostView(LoginRequiredMixin, CreateView):
    '''A view to handle creation of a new Post on an Profile'''

    # form class and template name
    form_class = CreatePostForm 
    template_name = "mini_insta/create_post_form.html"

    # create a URL to redirect users to after posting
    def get_success_url(self):
        '''Provides a URL to redirect to after creating a new Post'''

        # create and return a URL:
        #return reverse('show_all')
        profile_pk = Profile.objects.get(user=self.request.user).pk
        return reverse('show_profile', kwargs={'pk': profile_pk})
    
    # get context data for template use
    def get_context_data(self,**kwargs):
        '''return the dicitionary of context varaibles for use in the template'''

        # calling the superclass method
        context = super().get_context_data(**kwargs)

        # add the profile into the context dictionary 
        if self.request.user.is_authenticated:
            profile = Profile.objects.filter(user=self.request.user).first()
            context['profile'] = profile
        else:
            context['profile'] = None

        return context
    
    def get_login_url(self):
        '''return the UR for this app's login page'''

        return reverse('login')
    
    # handes form submission, creates new objects
    def form_valid(self, form):
        '''This method handles the form submission and saves the new objects to the Django datatabse'''

        profile = Profile.objects.get(user=self.request.user)

        # attach FK relations
        form.instance.profile = profile
        form.instance.user = self.request.user

        # save the Post object first
        response = super().form_valid(form)

        # handle uploaded image files
        files = self.request.FILES.getlist('image_files')  # 'image_files' = input name
        for f in files:
            Photo.objects.create(post=self.object, image_file=f)

        return response



# DeleteView for Posts
class DeletePostView(LoginRequiredMixin, DeleteView):
    '''View class to delete a comment on an Article'''

    model = Post
    template_name = "mini_insta/delete_post_form.html"

    # get context data for template use
    def get_context_data(self,**kwargs):
        '''return the dicitionary of context varaibles for use in the template'''

        # calling the superclass method
        context = super().get_context_data(**kwargs)
        
        # find and add profile to the context data
        post = self.get_object()
        profile = post.profile

        # add the profile into the context dictionary 
        context["profile"] = profile
        context["post"] = post

        return context
    
    # get the login url, must be logged in to do this
    def get_login_url(self):
        '''return the UR for this app's login page'''

        return reverse('login')

    # create a URL to redirect users to after posting
    def get_success_url(self):
        '''Return the URL to redirect to after a sucessful delete'''

        # find the PK for this Comment
        pk = self.kwargs['pk']

        # find the Comment Object
        post = Post.objects.get(pk=pk)

        # find pk of the article to which this comment is associated
        profile = post.profile

        return reverse('show_profile', kwargs={'pk':profile.pk})
    


# UpdateView for Posts
class UpdatePostView(LoginRequiredMixin, UpdateView):
    '''View class to handle update of an article based on its PK.'''

    model = Post
    form_class = UpdatePostForm
    template_name = "mini_insta/update_post_form.html"

    # get the login url, must be logged in to do this
    def get_login_url(self):
        '''return the UR for this app's login page'''

        return reverse('login')

    # create a URL to redirect users to after posting
    def get_success_url(self):
        '''Return the URL to redirect to after a sucessful delete'''

        # find the PK for this Comment
        pk = self.kwargs['pk']

        return reverse('show_post', kwargs={'pk':pk})
    

# ShowFollowersDetailView - a view to display all the details of the follower list 
class ShowFollowersDetailView(DetailView):
    '''A view to show the followers of a single Profile.'''

    model = Profile
    template_name = "mini_insta/show_followers.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        '''Return the dictionary of context variables for use in the template.'''
        # get the profiles
        context = super().get_context_data(**kwargs)
        profile = self.object

        # list of follower Profiles
        context["followers"] = profile.get_followers()

        return context
    

# ShowFollowingDetailView - a view to display all the details of the following list 
class ShowFollowingDetailView(DetailView):
    '''A view to show the users followed by a single Profile.'''

    model = Profile
    template_name = "mini_insta/show_following.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        '''Return the dictionary of context variables for use in the template.'''
        # get the profiles
        context = super().get_context_data(**kwargs)
        profile = self.object

        # list of Profiles being followed
        context["following"] = profile.get_following()

        return context
    

# PostFeedListView - a view to display all of the post on a profile's feed
class PostFeedListView(LoginRequiredMixin, ListView):
    '''Define a view class to show all mini_insta profiles'''

    # model type
    model = Post

    # html template
    template_name = "mini_insta/show_feed.html"

    # context
    context_object_name = "posts"

    # get the login url, must be logged in to do this
    def get_login_url(self):
        '''return the UR for this app's login page'''

        return reverse('login')

    def get_queryset(self):
        ''' get the feed for the user'''
        profile = Profile.objects.get(user=self.request.user)
        posts = list(profile.get_post_feed())  # force evaluation to a list

        # go over posts, see if liked by user
        for post in posts:
            post.liked_by_user = post.get_all_likes().filter(profile__user=self.request.user).exists()
        
        return posts
    

# SearchView - a view to get the search form or search results
class SearchView(LoginRequiredMixin, ListView):
    ''' Facilitates searching '''
    template_name = "mini_insta/search_results.html"
    context_object_name = "posts"

    def get_login_url(self):
        '''return the UR for this app's login page'''

        return reverse('login')

    # which template do we dispatch?
    def dispatch(self, request, *args, **kwargs):
        ''' dispatch proper template '''
        try:
            self.profile = Profile.objects.get(user=request.user)
        # just in case there's no profile for some reason
        except Profile.DoesNotExist:
            return render(request, "mini_insta/search.html", {"error": "Profile not found."})
        
        # get the query
        self.query = request.GET.get('query', None)

        # if there is none, show search form
        if not self.query:
            return render(request, "mini_insta/search.html", {"profile": self.profile})
        
        return super().dispatch(request, *args, **kwargs)
    

    # get the posts with matching captions
    def get_queryset(self):
        '''Return posts whose caption contains the search query'''
        return Post.objects.filter(caption__icontains=self.query)
    

    # query stuff 
    def get_context_data(self, **kwargs):
        ''' get the proper query'''
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            profile = Profile.objects.filter(user=self.request.user).first()
            context['profile'] = profile
        else:
            context['profile'] = None
        context['query'] = self.query

        context['matching_profiles'] = Profile.objects.filter(
            # complex query (in the django documentation)
            Q(username__icontains=self.query) |
            Q(display_name__icontains=self.query) |
            Q(bio_text__icontains=self.query)
        )

        return context
    
   
# allow following
class FollowView(LoginRequiredMixin, TemplateView):
    '''Facillitates following of a mini-insta profile'''

    def dispatch(self, request, *args, **kwargs):
        '''chooses how things get posted '''
        logged_in_profile = Profile.objects.filter(user=self.request.user).first()
        target_profile = get_object_or_404(Profile, pk=kwargs['pk'])

        # if has already followed before, dont creat a new relation
        if logged_in_profile != target_profile:
            Follower.objects.get_or_create(
                profile=target_profile,             # the one being followed
                follower_profile=logged_in_profile  # the one following
            )

        # using redirect because we're not really using a real form
        return redirect('show_profile', pk=target_profile.pk)


# allow unfollowing   
class DeleteFollowView(LoginRequiredMixin, TemplateView):
    '''Facillitates un following of a mini-insta profile'''

    def dispatch(self, request, *args, **kwargs):
        '''chooses how things get posted '''
        logged_in_profile = Profile.objects.filter(user=self.request.user).first()
        target_profile = get_object_or_404(Profile, pk=kwargs['pk'])

        # delete it 
        Follower.objects.filter(
            profile=target_profile,
            follower_profile=logged_in_profile
        ).delete()

        # using redirect because we're not really using a real form
        next_url = request.POST.get('next', reverse('show_profile', kwargs={'pk': target_profile.pk}))
        return redirect(next_url)
    


class LikeView(LoginRequiredMixin, TemplateView):
    '''Facillitates liking of a mini-insta post'''

    def dispatch(self, request, *args, **kwargs):
        '''chooses how things get posted '''
        logged_in_profile = Profile.objects.filter(user=self.request.user).first()
        post = get_object_or_404(Post, pk=kwargs['pk'])

        # if has already liked before, dont creat a new relation
        if post.profile != logged_in_profile:
            Like.objects.get_or_create(post=post, profile=logged_in_profile)

        # using redirect because we're not really using a real form
        next_url = request.POST.get('next', reverse('show_post', kwargs={'pk': post.pk}))
        return redirect(next_url)
    


class DeleteLikeView(LoginRequiredMixin, TemplateView):
    '''Facillitates unliking of a mini-insta post'''

    def dispatch(self, request, *args, **kwargs):
        '''chooses how things get posted '''
        logged_in_profile = Profile.objects.filter(user=self.request.user).first()
        post = get_object_or_404(Post, pk=kwargs['pk'])

        # delete it
        Like.objects.filter(post=post, profile=logged_in_profile).delete()

        # using redirect because we're not really using a real form
        next_url = request.POST.get('next', reverse('show_post', kwargs={'pk': post.pk}))
        return redirect(next_url)


class CreateCommentView(LoginRequiredMixin, CreateView):
    '''Facilitates creating a comment on a Post'''
    model = Comment
    form_class = CreateCommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        profile = Profile.objects.get(user=self.request.user)
        form.instance.post = post
        form.instance.profile = profile
        form.save()
        return redirect('show_post', pk=post.pk)

    def get_login_url(self):
        return reverse('login')
    

class DeleteCommentView(LoginRequiredMixin, DeleteView):
    '''Facilitates deleting a comment'''
    model = Comment
    template_name = "mini_insta/delete_comment_form.html"

    def get_login_url(self):
        return reverse('login')

    def get_success_url(self):
        # after deletion, go back to the post
        comment = self.get_object()
        post = comment.post
        return reverse('show_post', kwargs={'pk': post.pk})


