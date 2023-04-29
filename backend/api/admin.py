from django.contrib import admin
from .models import Music, Dlc, MusicPack, Pattern, PatternHistory


# Register your models here.
class MusicAdmin(admin.ModelAdmin):
    search_fields = ['name']

class DlcAdmin(admin.ModelAdmin):
    search_fields = ['name']

class MusicPackAdmin(admin.ModelAdmin):
    search_fields = ['name']

class PatternAdmin(admin.ModelAdmin):
    search_fields = ['music__name']


admin.site.register(Music, MusicAdmin)
admin.site.register(Dlc, DlcAdmin)
admin.site.register(MusicPack, MusicPackAdmin)
admin.site.register(Pattern, PatternAdmin)
admin.site.register(PatternHistory)
