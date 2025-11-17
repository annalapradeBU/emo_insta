# File: models.py
# Author: Anna LaPrade (alaprade@bu.edu), 09/23/2025
# Description: the models and their attributes for the mini_insta app

from django.db import models
from django.contrib.auth.models import User # for authentication1

# Create your models here.

# mini-insta profile model 
class Profile(models.Model):
    '''Encapsulate the data of a Profile by an user.'''

    # define the data attributed to this object 
    username = models.TextField(blank=True)
    display_name = models.TextField(blank=True)
    profile_image_url = models.URLField(blank=True)
    bio_text = models.TextField(blank=True)
    join_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # get all Posts associated with a Profile
    def get_all_posts(self):
        '''Return a QuerySet of Posts on this Profile'''
        posts = Post.objects.filter(profile=self).order_by('-timestamp')
        return posts
    
    # gets all Followers associated with a Profile 
    def get_followers(self):
        ''' Returns list of followers associated with this profile '''
        follower_query = Follower.objects.filter(profile=self)
        followers = [follower.follower_profile for follower in follower_query]

        return followers
    
    # gets the number of Followers associated with a Profile 
    def get_num_followers(self):
        '''Returns the number of Followers associated with a profile'''
        return Follower.objects.filter(profile=self).count()
    
    # gets all Profiles another Profile follows 
    def get_following(self):
        ''' Returns list of followed profies associated with this profile '''
        following_query = Follower.objects.filter(follower_profile=self)
        following = [follows.profile for follows in following_query]

        return following
    
    # gets the number all Profiles another Profile follows 
    def get_num_following(self):
        '''Returns the number of followed profiles associated with a profile'''
        return Follower.objects.filter(follower_profile=self).count()

    # gets the feed for a particular Profile
    def get_post_feed(self):
        following_profiles = self.get_following() + [self]

        # if they're aren't any, return none
        if not following_profiles:
            return Post.objects.none()
        
        # newest first
        return Post.objects.filter(profile__in=following_profiles).order_by('-timestamp')

    
    # string formatting
    def __str__(self):
        ''' return a strig representation of this model instance '''
        return f'{self.display_name}, username: {self.username}'
    

# mini-insta post model, one profile to many posts
class Post(models.Model):
    '''Encapsulate the idea of a Post on a Profile'''

    # data attribute for the Posts
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    caption = models.TextField(blank=False)

    # get all photos associated with a Post
    def get_all_photos(self):
        '''Return a QuerySet of Posts on this Profile'''
        photos = Photo.objects.filter(post=self).order_by('-timestamp')
        return photos
    
    # get all comments associated with a Post
    def get_all_comments(self):
        '''Return a QuerySet of comments on this Profile'''
        comments = Comment.objects.filter(post=self).order_by('-timestamp')
        return comments
    
    # get all likes associated with a Post
    def get_all_likes(self):
        '''Return a QuerySet of Likes on this Profile'''
        likes = Like.objects.filter(post=self).order_by('-timestamp')
        return likes
    
    # get the number of likes associated with a Post
    def get_like_count(self):
        """Return the number of likes for this post."""
        return Like.objects.filter(post=self).count()
    

    # string representation of a Post
    def __str__(self):
        ''' return a string representation of this Post instance '''
        return f'{self.caption} by {self.profile.username}'
    

# mini-insta photo model, one post to many photos
class Photo(models.Model):
    '''Encapsulate the idea of a Photo within a Post'''

    # data attribute for the Photo
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image_url = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    image_file = models.ImageField(blank=True)
    
    # string representation of a Photo
    def __str__(self):
        if self.image_url:
            image_source = self.image_url
        elif self.image_file:
            image_source = self.image_file.name
        else:
            image_source = 'No image'

        return f'Photo for "{self.post.caption}" - {image_source}'

    # get the image URL
    def get_image_url(self):
        '''Returns the URL of the image. '''

        if self.image_url:
            return self.image_url
        elif self.image_file:
            return self.image_file.url
        else:
            return None
        


# mini-insta Follow model
class Follower(models.Model):
    '''Encapsulate the idea of a Follower of a Profile'''

    # data attribute for the Photo
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile")
    follower_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="follower_profile")
    timestamp = models.DateTimeField(auto_now=True)

    # string representation of a Follower
    def __str__(self):
        ''' return a string representation of this Follower instance '''
        return f'{self.follower_profile.username} follows {self.profile.username}'
    
   

class Comment(models.Model):
    '''Encapsulate the idea of a Comment about a Post'''

    # data attribute for the Comments
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    text = models.TextField(blank=False)
    
    # string representation of a Comment
    def __str__(self):
        ''' return a string representation of this Comment instance '''
        return f'{self.text} by {self.profile.username} on {self.post.caption}'
    

class Like(models.Model):
    '''Encapsulate the idea of a Like about a Post'''

    # data attribute for the Likes
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    # string representation of a Like
    def __str__(self):
        ''' return a string representation of this Comment instance '''
        return f'{self.profile.username} liked {self.post.caption} on {self.timestamp}'


    