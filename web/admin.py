# admin.py
from django.contrib import admin
from .models import Quote, Source

admin.site.register(Quote)
admin.site.register(Source)
