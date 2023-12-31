from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response

# lets you directly manipulate database fields within database queries, leading to more efficient operations
from django.db.models import F

# Accessing Django Channels' channel layer for WebSocket integration
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from core.models import Notification, Hashtag


# --------------- NOTIFICATION API VIEWS ---------------

# Remove a specific notification from a user's WebSocket
def remove_notification(user_id, notification_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user_id}",
        {
            "type": "remove_notification",
            "unique_identifier": notification_id
        }
    )

# Utility function to handle follow-related notifications
def notify_user(notification_recipient, notification_sender, notification_type, message):
    # Create a notification for the recipient of the notification action
    try:
        notification = Notification.objects.create(
            recipient=notification_recipient,
            sender=notification_sender,
            notification_type=notification_type
        )
    except Exception as e:
        raise APIException()

    # Notify the recipient via WebSocket about the new notification
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{notification_recipient.id}",
            {
                "type": "core.notification",
                "unique_identifier": str(notification.id),
                "notification_type": notification_type,
                "recipient": str(notification_recipient.id),
                "sender": str(notification_sender.id),
                "message": f"{notification_sender.username} {message}",
                "sender_profile_picture_url": notification_sender.profile_picture.url if notification_sender.profile_picture else None,
            }
        )
    except Exception as e:
        raise APIException()


# Utility function to update follow counters
# following_user is the user being followed and follower_user is the user who is following
def update_follow_counters(following_user, follower_user):
    # Increment the num_followers counter for the user being followed (following_user) using Django F object
    following_user.num_followers = F('num_followers') + 1
    following_user.save()
    # Increment the num_following counter for the user attempting to follow (follower_user) using Django F object
    follower_user.num_following = F('num_following') + 1
    follower_user.save()


# --------------- POST API VIEWS ---------------

# Function that takes a list of hashtag names and creates or retrieves corresponding Hashtag objects.
    # It returns a list of Hashtag objects ids that are associated with the provided names.
def create_hashtags(hashtag_names):
    hashtag_ids = []  # Initialize an empty list to store the hashtag IDs
    for name in hashtag_names:
        hashtag, created = Hashtag.objects.get_or_create(name=name)
        hashtag_ids.append(hashtag.pk)  # Add the ID of the retrieved or newly created hashtag to the list
    return hashtag_ids  # Return the list of hashtag IDs


# --------------- Follow API VIEWS ---------------

def accept_follow_request_notification(notification, user, action):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user.id}",
        {
            "type": "notification_follow_request_accept",
            "action": action,
            "unique_identifier": str(notification.id),
        }
    )