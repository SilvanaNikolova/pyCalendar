from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.utils.text import slugify
from django.conf import settings
from django.dispatch import receiver

def upload_location(instance, filename):
    file_path = 'event/{created_user_id}/{name}-{filename}'.format(
        created_user_id=str(instance.created_user.id),
        name = str(instance.name),
        filename = filename
    )
    return file_path

class EventCategory(models.Model):
    PRIORITY = [
        ("H", "High"),
        ("M", "Medium"),
        ("L", "Low"),
    ]

    name = models.CharField(max_length=60, null=False, blank=False)
    description = models.TextField(max_length=255, null=False, blank=False)
    priority = models.CharField(max_length=10, choices=PRIORITY)
    image = models.ImageField(upload_to=upload_location, default='default/default_category_logo.png') ## TODO Test
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="date created")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="date updated")
    slug = models.SlugField(blank=True, unique=True)

    def __str__(self):
        return self.name
    

@receiver(post_delete, sender=EventCategory)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)

# Функцията задава url към категорията преди да бъде събмитната
def pre_save_event_category_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.created_user.username + "-" + instance.name)

pre_save.connect(pre_save_event_category_receiver, sender=EventCategory)

class Event(models.Model):
    STATUS = [
        ("future", "Future"),
        ("active", "Active"),
        ("past", "Past"),
    ]

    REPEAT_CHOICES = [
        ('none', 'No repeat'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=60, null=False, blank=False)
    description = models.TextField(max_length=200, null=False, blank=False)
    status = models.CharField(max_length=10, choices=STATUS)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    repeat = models.CharField(max_length=10, choices=REPEAT_CHOICES, default='none')
    end_repeat_date = models.DateField(null=True, blank=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="date created")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="date updated")
    slug = models.SlugField(blank=True, unique=True)

    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='events', blank=True)

    def __str__(self):
        return self.name
    

# Функцията задава url към категорията преди да бъде събмитната
def pre_save_event_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.created_user.username + "-" + instance.name)

pre_save.connect(pre_save_event_receiver, sender=Event)
