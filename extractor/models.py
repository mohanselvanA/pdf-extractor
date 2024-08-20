from django.db import models

class Disease(models.Model):
    name = models.CharField(max_length=225, unique=True)
    code = models.CharField(max_length=50)

    def __str__(self):
        return self.name
