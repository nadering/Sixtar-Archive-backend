from django.contrib import admin
from .models import Music, Dlc, MusicPack, Pattern, PatternHistory


# Register your models here.
class BaseReadOnlyAdminMixin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class MusicAdmin(admin.ModelAdmin):
    search_fields = ['name']

class DlcAdmin(admin.ModelAdmin):
    search_fields = ['name']

class MusicPackAdmin(admin.ModelAdmin):
    search_fields = ['name']

class PatternAdmin(admin.ModelAdmin):
    search_fields = ['music__name']

class PatternHistoryAdmin(BaseReadOnlyAdminMixin, admin.ModelAdmin):
    search_fields = ['=music_id']


admin.site.register(Music, MusicAdmin)
admin.site.register(Dlc, DlcAdmin)
admin.site.register(MusicPack, MusicPackAdmin)
admin.site.register(Pattern, PatternAdmin)
admin.site.register(PatternHistory, PatternHistoryAdmin)
