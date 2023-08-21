from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

# lets you directly manipulate database fields within database queries, leading to more efficient operations
from django.db.models import F
# Atomic transactions ensure that a series of database operations are completed together or not at all, maintaining data integrity.
from django.db import transaction

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from core.models import Post, Comment, Notification
from core.serializers import CommentSerializer
from api_utility_functions import get_pagination_indeces


# Endpoint: /api/comment/post/{post_id}
# API view to create a comment on a specific post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    content = request.data.get('content')

    if not content:
        return Response({"error": "Comment content is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Use an atomic transaction for creating the Comment instance, updating the comment counter,
        # creating a notification, and informing the WebSocket of the comment creation
        with transaction.atomic():
            # Create comment for the post
            comment = Comment.objects.create(user=request.user, post=post, content=content)
            serializer = CommentSerializer(comment)

            # Increment the counter for the comment count
            post.comment_count = F('comment_count') + 1
            post.save()  # Save the post to update the counter

            # Create a new_comment notification for the post author
            notification = Notification.objects.create(
                recipient=post.user,  # Author of the post
                sender=request.user,
                notification_type='new_comment',
                notification_post=post,
                notification_comment=comment
            )

            # Notify the post author via WebSocket about the new comment
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{post.user.id}",
                {
                    "type": "notification",
                    "unique_identifier": str(notification.id),
                    "notification_type": "new_comment",
                    "recipient": str(post.user.id),
                    "sender": str(request.user.id),
                    "message": f"{request.user.username} commented on your post",
                    "sender_profile_picture_url": request.user.profile_picture.url if request.user.profile_picture else None,
                    "post_media_url": post.media.url if post.media else None,
                }
            )
    except Exception as e:
        return Response({"error": "An error occurred while creating the comment"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


# Endpoint: /api/comment/{comment_id}/
# API view to delete a specific comment
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if the requesting user is the owner of the comment or the owner of the post
    if comment.user != request.user and comment.post.user != request.user:
        raise PermissionDenied("You don't have permission to delete this comment")

    try:
        # Use an atomic transaction for deleting the Comment instance, updating the comment counter,
        # deleting the comment notification, and informing the WebSocket of the deletion
        with transaction.atomic():
            comment.delete()

            # Decrement the counter for the comment count
            comment.post.comment_count = F('comment_count') - 1
            comment.post.save()  # Save the post to update the counter

            # Fetch the associated 'new_comment' notification
            notification = Notification.objects.filter(
                recipient=comment.post.user,
                sender=request.user,
                notification_type='new_comment',
                notification_post=comment.post
            ).first()

            # Check if the notification exists
            if notification:
                notification_id = str(notification.id)  # Store the ID for WebSocket use
                notification.delete()

                # Remove the notification for the post author via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{comment.post.user.id}",
                    {
                        "type": "remove_notification",
                        "unique_identifier": notification_id
                    }
                )
    except Exception as e:
        return Response({"error": "An error occurred while deleting the comment"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Endpoint: /api/comments/post/{post_id}/?page={}&page_size={}
# API view to view all the comments for a specific post
@api_view(['GET'])
def get_post_comments(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    # Set a default page size of 20 returned datasets per page
    default_page_size = 20
    # Utility function to get current page number and page size from the request's query parameters and calculate the pagination slicing indeces
    start_index, end_index, validation_response = get_pagination_indeces(request, default_page_size)
    if validation_response:
        return validation_response

    # Access comments for the specified post using the related_name
    comments = post.post_comments[start_index:end_index]
    serializer = CommentSerializer(comments, many=True, context={'request': request})

    return Response(serializer.data, status=status.HTTP_200_OK)
