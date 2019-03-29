from __future__ import unicode_literals

from django.contrib import admin





class TagAdmin(admin.ModelAdmin):

    list_display = ["name", "slug"]
    ordering = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}



