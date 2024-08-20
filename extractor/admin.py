from django.contrib import admin

# Register your models here.
from .models import Disease



class DiseaseAdmin(admin.ModelAdmin):
    pass


admin.site.register(Disease, DiseaseAdmin)