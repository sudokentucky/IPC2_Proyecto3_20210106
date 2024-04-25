"""
URL configuration for FrontEnd project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from FrontEnd import views

urlpatterns = [
    path('', views.home, name='home'),
    path('informacion', views.informacion, name='informacion'),
    path('grabarConfiguracion', views.grabarConfiguracion, name='grabarConfiguracion'),
    path('grabarTransaccion', views.grabarTransaccion, name='grabarTransaccion'),
    path('limpiarDatos', views.limpiar_datos, name='limpiarDatos'),
    path('devolverEstadoCuenta', views.devolverEstadoCuenta, name='devolverEstadoCuenta'),
    path('consultarIngresos', views.consultar_ingresos, name='consultarIngresos'),
    path('documentacion', views.documentacion, name='documentacion')
]