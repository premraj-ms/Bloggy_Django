from django.db import models

# Create your models here.
class Categories(models.Model):
    catName = models.CharField(max_length=60, null=True, blank=True)
    catIcon = models.CharField(max_length=60, null=True, blank=True)
    catColor = models.CharField(max_length=60, null=True, blank=True)
    catSlug = models.CharField(max_length=60, null=True, blank=True)
    catDescription = models.CharField(max_length=200, null=True, blank=True)
    catCreated = models.DateField(auto_now_add=True, null=True)  # Use only auto_now_add
