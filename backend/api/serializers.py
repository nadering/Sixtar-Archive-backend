from rest_framework import serializers
from api.models import Music, Dlc, MusicPack, Pattern, PatternHistory


class MusicSerializer(serializers.ModelSerializer):
  class Meta:
    model = Music
    fields = '__all__'


class DlcSerializer(serializers.ModelSerializer):
  class Meta:
    model = Dlc
    fields = '__all__'
   
    
class MusicPackSerializer(serializers.ModelSerializer):
  class Meta:
    model = MusicPack
    fields = '__all__'


class PatternSerializer(serializers.ModelSerializer):
  class Meta:
    model = Pattern
    fields = '__all__'


class PatternInfoSerializer(serializers.Serializer):
  musicId       = serializers.IntegerField(source='music_id')
  name          = serializers.CharField()
  composer      = serializers.CharField()
  dlcName       = serializers.CharField(source='dlc_name')
  dlcCode       = serializers.CharField(source='dlc_code')
  musicPackName = serializers.CharField(source='music_pack_name')
  musicPackId   = serializers.IntegerField(source='music_pack_id')
  type          = serializers.CharField()


class FloorSerializer(serializers.Serializer):
  floor    = serializers.FloatField()
  patterns = PatternInfoSerializer(many=True)
  
  
class DifficultySerializer(serializers.Serializer):
  difficulty = serializers.IntegerField()
  floors     = FloorSerializer(many=True)


class BoardSerializer(serializers.Serializer):
  mode          = serializers.CharField()
  minDifficulty = serializers.IntegerField(source='min_difficulty')
  maxDifficulty = serializers.IntegerField(source='max_difficulty')
  patternCount  = serializers.IntegerField(source='pattern_count')
  board         = DifficultySerializer(many=True, read_only=True)


class PatternHistorySerializer(serializers.ModelSerializer):
  class Meta:
    model = PatternHistory
    fields = '__all__'