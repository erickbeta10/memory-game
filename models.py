from django.db import models
# Importamos el modelo de Usuario que Django ya trae (para login)
from django.contrib.auth.models import User

# --- Modelo para las Estadísticas del Jugador ---
# Este modelo "extiende" al usuario de Django para agregarle
# los campos de estadísticas que pide el proyecto.
class PlayerStatistics(models.Model):
    # Usamos OneToOneField para vincular esta estadística a un único usuario.
    # on_delete=models.CASCADE significa que si se borra el usuario,
    # se borran también sus estadísticas.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='stats')

    # Campos que pide la rúbrica [cite: 107-111]
    total_victories = models.IntegerField(default=0)
    total_defeats = models.IntegerField(default=0)
    total_games_played = models.IntegerField(default=0)

    # Guardamos el tiempo total en segundos y luego calculamos el promedio
    total_time_seconds = models.FloatField(default=0.0) 

    # Contadores para saber cuál es el nivel más jugado
    games_basic = models.IntegerField(default=0)
    games_medium = models.IntegerField(default=0)
    games_advanced = models.IntegerField(default=0)

    def __str__(self):
        return f"Estadísticas de {self.user.username}"

    # Propiedad para calcular el nivel más jugado [cite: 111]
    @property
    def most_played_level(self):
        levels = {
            'Básico': self.games_basic,
            'Medio': self.games_medium,
            'Avanzado': self.games_advanced
        }
        # Si todos son 0, no hay uno "más jugado"
        if all(v == 0 for v in levels.values()):
            return "N/A"
        # Encuentra el nombre del nivel con el valor más alto
        return max(levels, key=levels.get)

    # Propiedad para calcular el tiempo promedio [cite: 110]
    @property
    def average_time(self):
        if self.total_games_played == 0:
            return 0.0
        return self.total_time_seconds / self.total_games_played

# --- Modelo para el Historial de Partidas ---
# Esto guardará un registro de CADA partida individual 
class GameRecord(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_records')
    level_choices = [
        ('Básico', 'Básico'),
        ('Medio', 'Medio'),
        ('Avanzado', 'Avanzado'),
    ]
    level = models.CharField(max_length=10, choices=level_choices)

    was_won = models.BooleanField() # True si ganó, False si perdió
    time_taken = models.FloatField() # Tiempo en segundos
    date_played = models.DateTimeField(auto_now_add=True) # Fecha y hora

    def __str__(self):
        status = "Victoria" if self.was_won else "Derrota"
        return f"Partida de {self.player.username} - {self.level} ({status})"