from django.contrib import admin
from .models import Chat, Query, Document, QueryFeedBack

# Register your models here.
admin.site.register(Chat)
admin.site.register(Query)
admin.site.register(Document)
admin.site.register(QueryFeedBack)
