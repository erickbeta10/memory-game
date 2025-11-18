from django.urls import path
from . import views

app_name = 'memory_game'

urlpatterns = [
    # Rutas de autenticación
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Ruta principal y del juego
    path('', views.home_view, name='home'), 
    path('juego/<str:level>/', views.game_view, name='game'),

    # --- RUTA API (Debe estar aquí) ---
    path('save_result/', views.save_game_result, name='save_result'),
]