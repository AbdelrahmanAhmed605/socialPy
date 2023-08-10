from rest_framework import serializers
from .models import User, Hashtag, Post, Comment, Follow, Message


# Serializers to convert Django model instances into Python data types and vice versa (deserialization)
# Python data will be rendered into JSON for use in API responses (serialization)
# JSON data will be converted to python data from API requests to be saved in Django model instances. (deserialization)

class UserSerializer(serializers.ModelSerializer):
    # Create new fields containing the number of followers, following, and posts for a user
    num_followers = serializers.SerializerMethodField()
    num_following = serializers.SerializerMethodField()
    num_posts = serializers.SerializerMethodField()

    # Function to count the number of followers for a specific user
    # followers is a related_name field in the Follow model for the User field foreign key
    def get_num_followers(self, obj):
        return obj.followers.count()

    # Function to count the number of following for a specific user
    # following is a related_name field in the Follow model for the User field foreign key
    def get_num_following(self, obj):
        return obj.following.count()

    # Function to count the number of posts for a specific user
    # user_posts is a related_name field in the Post model for the User field foreign key
    def get_num_posts(self, obj):
        return obj.user_posts.count()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_picture', 'bio', 'contact_information', 'profile_privacy', 'num_followers', 'num_following', 'num_posts']


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    # Define hashtags field as a list of strings, each with a max length of 50 characters
    hashtags = serializers.ListField(child=serializers.CharField(max_length=50))

    # Custom field to indicate if the requesting user has liked the post
    liked_by_user = serializers.SerializerMethodField()

    # Create new fields containing the number of likes and comments for a post
    num_likes = serializers.SerializerMethodField()
    num_comments = serializers.SerializerMethodField()

    # Function to count the number of likes for a specific post
    def get_num_likes(self, obj):
        return obj.likes.count()

    # Function to count the number of comments for a specific post
    # post_comments is the related_name field in the Comment model for the Post field foreign key
    def get_num_comments(self, obj):
        return obj.post_comments.count()

    # Function that takes a list of hashtag names and creates or retrieves corresponding Hashtag objects.
    # It returns a list of Hashtag objects that are associated with the provided names.
    def create_hashtags(self, hashtag_names):
        hashtags = []  # Initialize an empty list to store the hashtag objects
        for name in hashtag_names:
            # Try to retrieve an existing hashtag with the given name, or create a new one
            hashtag, created = Hashtag.objects.get_or_create(name=name)
            hashtags.append(hashtag)  # Add the retrieved or newly created hashtag to the list
        return hashtags  # Return the list of hashtag objects

    # Function that checks if a requesting user liked the post that is being retrieved
    # This will be used on the front end to provide indication to users if they liked a post or not
    def get_liked_by_user(self, post):
        if 'request' in self.context:
            user = self.context['request'].user
            return post.likes.filter(id=user.id).exists()
        return None

    class Meta:
        model = Post
        fields = ['user', 'content', 'media', 'visibility', 'hashtags', 'created_at', 'updated_at', 'likes', 'num_likes', 'num_comments', 'liked_by_user']


class CommentSerializer(serializers.ModelSerializer):
    # Custom field to indicate whether the requesting user can edit the comment
    can_edit = serializers.SerializerMethodField()
    # Custom field to indicate whether the requesting user can delete the comment
    can_delete = serializers.SerializerMethodField()

    def get_can_delete(self, comment):
        if 'request' in self.context:
            # Check if the requesting user is the owner of the comment or the owner of the post
            user = self.context['request'].user
            return comment.user == user or comment.post.user == user
        return None

    def get_can_edit(self, comment):
        if 'request' in self.context:
            # Check if the requesting user is the owner of the comment
            user = self.context['request'].user
            return comment.user == user
        return None

    class Meta:
        model = Comment
        fields = ['user', 'post', 'content', 'created_at', 'updated_at', 'can_edit', 'can_delete']


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
