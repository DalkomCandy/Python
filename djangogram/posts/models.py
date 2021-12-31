from django.db import models
from djangogram.users import models as user_model
# Create your models here.
class TimestamedModel(models.Model):
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Post(TimestamedModel):
    author = models.ForeignKey(
        user_model.User,
        null = True,
        on_delete = models.CASCADE,
        related_name = 'post_auther'
        )
    image = models.ImageField(blank=True)
    caption = models.TextField(blank=True)
    image_likes = models.ManyToManyField(user_model.User, related_name = 'post_image_likes')

class comment(TimestamedModel):
    author = models.ForeignKey(
        user_model.User,
        null = True,
        on_delete = models.CASCADE,
        related_name = 'comment_auther'   
        )

    posts = models.ForeignKey(
        Post,
        null = True,
        on_delete = models.CASCADE,
        related_name = 'post_auther'
        )

    contents = models.TextField(blank=True)
