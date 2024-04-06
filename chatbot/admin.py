from django.contrib import admin
from .models import Chat, Query, Document, GoodResponse, BadResponse

# Register your models here.
admin.site.register(Chat)
admin.site.register(Query)
admin.site.register(Document)
admin.site.register(GoodResponse)
admin.site.register(BadResponse)
