from django.contrib import admin
from django.urls import path, include  # <--- Importe o 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pesquisas.urls')),  # <--- Adicione esta linha
]