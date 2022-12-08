from django.contrib import admin

from .models import NewsLetter, NewsLetterSubscribe


class NewsLetterAdmin(admin.ModelAdmin):
    list_display = ["title", "body", "tag_list"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags")

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())


admin.site.register(NewsLetter, NewsLetterAdmin)
admin.site.register(NewsLetterSubscribe)
