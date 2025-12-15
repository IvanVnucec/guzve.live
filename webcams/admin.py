from django.contrib import admin
from django.utils.html import format_html_join, format_html
from .models import Category, Group, Webcam, CongestionEstimate

class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "key"]
    search_fields = ["name", "key"]
    readonly_fields = ["groups"]

class GroupAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "webcams"]
    search_fields = ["title"]

    def webcams(self, obj) -> str:
        if not obj.pk:
            return "-"
        return format_html_join(
            " ",
            '<a href="{}" target="_blank" title="{}">'
            '<img src="{}" loading="lazy" width="60" height="45" style="object-fit:fill;border-radius:4px;">'
            '</a>',
            ((cam.image_url, cam.title, cam.image_url) for cam in obj.webcams.all().order_by('id'))
        ) or "—"
    webcams.short_description = "Webcams"

class WebcamAdmin(admin.ModelAdmin):
    list_display = ["title", "group", "last_update", "preview"]
    search_fields = ["title"]
    readonly_fields = ["preview_large"]

    def preview_large(self, obj) -> str:
        if not obj.pk:
            return "-"
        return self.preview(obj, w=obj.image_width, h=obj.image_height)

    def preview(self, obj, w=60, h=45) -> str:
        if not obj.pk:
            return "-"
        return format_html(
            '<a href="{}" target="_blank" title="{}">'
            '<img src="{}" loading="lazy" width="{}" height="{}" style="object-fit:fill;border-radius:4px;">'
            '</a>',
            obj.image_url, obj.title, obj.image_url, w, h
        ) or "—"
    preview.short_description = "Preview"

admin.site.register(Category, CategoryAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Webcam, WebcamAdmin)
admin.site.register(CongestionEstimate)
