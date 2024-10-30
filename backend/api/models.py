from django.db import models


class Dlc(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=45)
    code = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'dlc'
    
    def __str__(self):
      return self.name


class Music(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    composer = models.CharField(max_length=100)
    dlc = models.ForeignKey(Dlc, models.DO_NOTHING, blank=True, null=True)
    music_pack = models.ForeignKey('MusicPack', models.DO_NOTHING, blank=True, null=True)
    bpm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    bpm_min = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    bpm_max = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'music'
    
    def __str__(self):
      return self.name


class MusicPack(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=45)
    price = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'music_pack'
    
    def __str__(self):
      return self.name


class Pattern(models.Model):
    music = models.OneToOneField(Music, models.DO_NOTHING, primary_key=True)
    lunar_comet = models.IntegerField(blank=True, null=True)
    lunar_nova = models.IntegerField(blank=True, null=True)
    lunar_supernova = models.IntegerField(blank=True, null=True)
    lunar_quasar = models.IntegerField(blank=True, null=True)
    lunar_starlight = models.IntegerField(blank=True, null=True)
    lunar_f_comet = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    lunar_f_nova = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    lunar_f_supernova = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    lunar_f_quasar = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    lunar_f_starlight = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    solar_comet = models.IntegerField(blank=True, null=True)
    solar_nova = models.IntegerField(blank=True, null=True)
    solar_supernova = models.IntegerField(blank=True, null=True)
    solar_quasar = models.IntegerField(blank=True, null=True)
    solar_starlight = models.IntegerField(blank=True, null=True)
    solar_f_comet = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    solar_f_nova = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    solar_f_supernova = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    solar_f_quasar = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    solar_f_starlight = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pattern'
    
    def __str__(self):
      return f'{self.music.name} - Pattern'


class PatternHistory(models.Model):
    action = models.CharField(max_length=8, blank=True, null=True)
    revision = models.IntegerField()
    dt_datetime = models.DateTimeField()
    music_id = models.IntegerField(primary_key=True)  
    lunar_comet = models.IntegerField(blank=True, null=True)
    lunar_nova = models.IntegerField(blank=True, null=True)
    lunar_supernova = models.IntegerField(blank=True, null=True)
    lunar_quasar = models.IntegerField(blank=True, null=True)
    lunar_starlight = models.IntegerField(blank=True, null=True)
    lunar_f_comet = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    lunar_f_nova = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    lunar_f_supernova = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    lunar_f_quasar = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    lunar_f_starlight = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    solar_comet = models.IntegerField(blank=True, null=True)
    solar_nova = models.IntegerField(blank=True, null=True)
    solar_supernova = models.IntegerField(blank=True, null=True)
    solar_quasar = models.IntegerField(blank=True, null=True)
    solar_starlight = models.IntegerField(blank=True, null=True)
    solar_f_comet = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    solar_f_nova = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    solar_f_supernova = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    solar_f_quasar = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    solar_f_starlight = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pattern_history'
        constraints = [
            models.UniqueConstraint(
                fields=['music_id', 'revision'], name='history-constraint'),
            ]
    
    def __str__(self):
        return f'Music_id {self.music_id} - History #{self.revision}'


class Vote(models.Model):
    title = models.CharField(max_length=100)
    context = models.CharField(max_length=200, blank=True, null=True)
    solar_link = models.CharField(max_length=200)
    lunar_link = models.CharField(max_length=200)
    deadline = models.DateField()
    created_time = models.DateField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'vote'

    def __str__(self):
        return f'Vote {self.id} - {self.title}'
