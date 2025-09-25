from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Story, Like, Comment, Follower, Notification


@receiver(pre_save, sender=Story)
def mark_publish_transition(sender, instance: Story, **kwargs):
    # For updates, determine if status is transitioning to 'published'
    if instance.pk:
        try:
            previous = Story.objects.get(pk=instance.pk)
            instance._status_changed_to_published = (
                previous.status != 'published' and instance.status == 'published'
            )
        except Story.DoesNotExist:
            instance._status_changed_to_published = instance.status == 'published'
    else:
        # On create, it's considered a publish if created directly as published
        instance._status_changed_to_published = instance.status == 'published'


def _notify_followers_of_story_publish(story: Story) -> None:
    author = story.author
    follower_qs = Follower.objects.filter(followed=author).select_related('follower')
    notifications = [
        Notification(
            recipient=relation.follower,
            sender=author,
            notif_type='story',
            story=story,
        )
        for relation in follower_qs
    ]
    if notifications:
        Notification.objects.bulk_create(notifications, ignore_conflicts=True)


@receiver(post_save, sender=Story)
def create_notifications_on_story_publish(sender, instance: Story, created: bool, **kwargs):
    # Notify when a story is created as published, or when an existing story transitions to published
    if getattr(instance, '_status_changed_to_published', False):
        _notify_followers_of_story_publish(instance)


@receiver(post_save, sender=Like)
def create_notification_on_like(sender, instance: Like, created: bool, **kwargs):
    if not created:
        return
    story = instance.story
    sender_user = instance.user
    recipient = story.author
    if recipient == sender_user:
        return
    Notification.objects.create(
        recipient=recipient,
        sender=sender_user,
        notif_type='like',
        story=story,
    )


@receiver(post_save, sender=Comment)
def create_notification_on_comment(sender, instance: Comment, created: bool, **kwargs):
    if not created:
        return
    story = instance.story
    sender_user = instance.author
    recipient = story.author
    if recipient == sender_user:
        return
    Notification.objects.create(
        recipient=recipient,
        sender=sender_user,
        notif_type='comment',
        story=story,
        comment=instance,
    )

