from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils.text import slugify
from django.urls import reverse


class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(
        max_length=100, unique_for_date='created_at', blank=True)
    content = models.TextField(validators=[
        MinLengthValidator(
            100, message="Content must be at least 100 characters long."),
        MaxLengthValidator(
            10000, message="Content cannot exceed 10000 characters.")
    ])
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    banner = models.URLField(
        max_length=500, blank=True, null=True)
    image_name = models.CharField(max_length=500, blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)

    def total_likes(self):
        return self.likes.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.id, 'slug': self.slug})

    class Meta:
        ordering = ['-created_at']
