from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json 

from .models import PlayerStatistics, GameRecord 


# --- Vista para la Página Principal (Perfil/Home) ---
@login_required
def home_view(request):
    # Obtener o crear estadísticas
    stats, created = PlayerStatistics.objects.get_or_create(user=request.user)
    # Obtener el historial de partidas (últimas 10)
    records = request.user.game_records.all().order_by('-date_played')[:10] 
    
    context = {
        'user': request.user,
        'stats': stats,
        'records': records,
    }
    return render(request, 'memory_game/home.html', context)


# --- Vista para el Inicio de Sesión ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('memory_game:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('memory_game:home')
    else:
        form = AuthenticationForm()
        
    return render(request, 'memory_game/login.html', {'form': form})


# --- Vista para el Registro de Nuevos Usuarios ---
def register_view(request):
    if request.user.is_authenticated:
        return redirect('memory_game:home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            PlayerStatistics.objects.create(user=user)
            login(request, user)
            return redirect('memory_game:home')
    else:
        form = UserCreationForm()
        
    return render(request, 'memory_game/register.html', {'form': form})


# --- Vista para Cerrar Sesión ---
def logout_view(request):
    logout(request)
    return redirect('memory_game:login')


# --- Vista para la Pantalla del Juego (CORREGIDA) ---
@login_required 
def game_view(request, level):
    # [cite_start]Determinamos los intentos y el tiempo según el nivel [cite: 97-99, 104]
    if level == 'basico':
        attempts = 6
        time_limit_seconds = 60 
    elif level == 'medio':
        attempts = 4
        time_limit_seconds = 60
    elif level == 'avanzado':
        attempts = 2
        time_limit_seconds = 60
    else:
        # Si el nivel no existe, redirigir al home
        return redirect('memory_game:home')

    context = {
        'level': level,
        'attempts_left': attempts,
        'time_limit_seconds': time_limit_seconds,
        'board_size': 4, # Es 4x4 para todos
    }
    
    # ESTO ES LO QUE FALTABA: RETORNAR LA PLANTILLA
    return render(request, 'memory_game/game.html', context) # <-- La línea faltante


# --- VISTA PARA GUARDAR RESULTADOS (API) ---
@require_POST
@login_required
def save_game_result(request):
    try:
        data = json.loads(request.body)
        did_win = data.get('did_win')
        time_taken = data.get('time_taken')
        level = data.get('level')

        stats = PlayerStatistics.objects.get(user=request.user)
        
        # 1. Guardar registro de la partida (GameRecord)
        GameRecord.objects.create(
            player=request.user,
            level=level.capitalize(), 
            was_won=did_win,
            time_taken=time_taken
        )

        # 2. Actualizar estadísticas (PlayerStatistics)
        stats.total_games_played += 1
        stats.total_time_seconds += time_taken

        if did_win:
            stats.total_victories += 1
        else:
            stats.total_defeats += 1

        if level == 'basico':
            stats.games_basic += 1
        elif level == 'medio':
            stats.games_medium += 1
        elif level == 'avanzado':
            stats.games_advanced += 1

        stats.save() 

        return JsonResponse({'status': 'success', 'message': 'Resultados guardados correctamente.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)