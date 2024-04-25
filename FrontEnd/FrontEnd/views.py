from django.shortcuts import render
from django.http import HttpResponse
import requests
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

# URL base de la API de Flask
FLASK_API_URL = 'http://localhost:5000/api'

def home(request):
    return render(request, 'home.html')
def informacion(request):

    return render(request, 'informacion.html')

def grabarConfiguracion(request):
    if request.method == 'POST':
        xml_file = request.FILES['configFile']
        xml_string = xml_file.read().decode('utf-8')
        response = requests.post(f'{FLASK_API_URL}/grabarConfiguracion', data=xml_string)

        if response.status_code == 200:
            # Parsea y formatea el XML para indentarlo
            reparsed = parseString(response.content)
            formatted_xml = reparsed.toprettyxml(indent="  ")

            # Parsea el XML para extraer las listas de datos
            root = ET.fromstring(response.content)
            creados_clientes = [cliente.text for cliente in root.findall('clientes/creados/cliente')]
            actualizados_clientes = [cliente.text for cliente in root.findall('clientes/actualizados/cliente')]
            creados_bancos = [banco.text for banco in root.findall('bancos/creados/banco')]
            actualizados_bancos = [banco.text for banco in root.findall('bancos/actualizados/banco')]

            return render(request, 'configuracion.html', {
                'response_xml': formatted_xml,
                'creados_clientes': creados_clientes,
                'actualizados_clientes': actualizados_clientes,
                'creados_bancos': creados_bancos,
                'actualizados_bancos': actualizados_bancos,
            })
        else:
            return render(request, 'configuracion.html', {'response_xml': 'Error al recibir datos del servidor'})
    else:
        return render(request, 'configuracion.html')
    
def grabarTransaccion(request):
    if request.method == 'POST':
        xml_file = request.FILES['transacFile']
        xml_string = xml_file.read().decode('utf-8')
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(f'{FLASK_API_URL}/grabarTransaccion', data=xml_string, headers=headers)

        if response.status_code == 200:
            # Parsea y formatea el XML para indentarlo
            reparsed = parseString(response.content)
            formatted_xml = reparsed.toprettyxml(indent="  ")

            # Parsea el XML para extraer las listas de datos
            root = ET.fromstring(response.content)
            creadas_facturas = [factura.text for factura in root.findall('facturas/creadas/factura')]
            creados_pagos = [pago.text for pago in root.findall('pagos/creados/pago')]

            return render(request, 'transaccion.html', {
                'response_xml': formatted_xml,
                'creadas_facturas': creadas_facturas,
                'creados_pagos': creados_pagos,
            })
        else:
            return render(request, 'transaccion.html', {'response_xml': 'Error al recibir datos del servidor'})
    else:
        return render(request, 'transaccion.html')
    
def limpiar_datos(request):
    return render(request, 'limpiar.html')

def documentacion(request):
    return render(request, 'documentacion.html')

def devolverEstadoCuenta(request):
    data = []                                                                           
    error = None
    if request.method == 'GET':
        params = {}
        if 'NIT' in request.GET and request.GET['NIT']:
            params['NIT'] = request.GET.get('NIT')
        response = requests.get(f'{FLASK_API_URL}/devolverEstadoCuenta', params=params)
        xml = ET.fromstring(response.text)
        for cliente in xml.findall('cliente'):
            if 'NIT' in params and cliente.find('NIT').text != params['NIT']:
                continue
            cliente_data = {
                'cliente': cliente.find('NIT').text,
                'nombre': cliente.find('nombre').text,
                'saldo': cliente.find('saldo').text,
                'transacciones': [
                    {
                        'fecha': transaccion.find('fecha').text,
                        'cargo': transaccion.find('descripcion').text,
                        'abono': transaccion.find('valor').text,
                    }
                    for transaccion in cliente.findall('transacciones/transaccion')
                ],
            }
            data.append(cliente_data)
        if not data:
            error = 'No se encontraron datos para el NIT proporcionado.'
    return render(request, 'EstadoCuenta.html', {'response': data, 'error': error})

def consultar_ingresos(request):
        return render(request, 'ingresos.html')