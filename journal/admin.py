from django.contrib import admin
from .models import Horse, Rider, JournalEntry, Comment


@admin.register(Horse)
class HorseAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ('name', 'horse', 'created_at')
    list_filter = ('horse',)
    search_fields = ('name', 'horse__name')


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('rider', 'created_at', 'alerted_michelle')
    list_filter = ('alerted_michelle', 'created_at')
    search_fields = ('rider__name', 'rider__horse__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('entry', 'created_at')
    search_fields = ('entry__rider__name', 'text')
    readonly_fields = ('created_at',)
