from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Post(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    text = models.CharField(max_length=200)
    post_date = models.DateTimeField()

    def __str__(self):
        return f'id={self.id}'

class Comment(models.Model):
    text = models.CharField(max_length=200)
    creation_time = models.DateTimeField()
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, default=None, on_delete=models.PROTECT)

    def __str__(self):
        return f'id={self.id}'

class Profile(models.Model):
    bio = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)
    following = models.ManyToManyField(User, related_name="followers")
    
    def __str__(self):
        return f'id={self.id}'