from django.db import models

# Create your models here.
class Product(models.Model):
    title       = models.CharField(max_length=120, ) # max_length is required for charfield
    description = models.TextField()
    price       = models.DecimalField(decimal_places=2, max_digits=200) # 소숫점 2자리
    summary     = models.TextField(blank=True, null=False)
    featured    = models.BooleanField()