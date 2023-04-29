from django.urls import path

from api.views import MusicListAPI, DlcListAPI, MusicPackListAPI, PatternListAPI, BoardAPI, PatternHistoryListAPI


urlpatterns = [
    path('dlc', DlcListAPI.as_view()),
    path('music', MusicListAPI.as_view()),
    path('music-pack', MusicPackListAPI.as_view()),
    path('pattern', PatternListAPI.as_view()),
    path('board', BoardAPI.as_view()),
    path('pattern-history', PatternHistoryListAPI.as_view()),
]
