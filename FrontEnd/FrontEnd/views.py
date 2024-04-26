from django.shortcuts import render
from django.http import HttpResponse
import requests
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from xml.dom import minidom
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from collections import defaultdict
import numpy as np
import base64
from io import BytesIO

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
    
def limpiarDatos(request):
    message = ""  # Inicializar el mensaje como vacío

    if request.method == 'POST':
        response = requests.get(f'{FLASK_API_URL}/limpiarDatos')
        if response.status_code == 200 and response.text:
            xml = minidom.parseString(response.text).toprettyxml()
            message = xml
        else:
            message = 'Error: ' + response.text

    return render(request, 'limpiar.html', {'message': message})


def documentacion(request):
    return render(request, 'documentacion.html')

def devolverEstadoCuenta(request):
    data = []                                                                           
    error = None

    if request.method == 'POST':
        params = {}
        if 'NIT' in request.POST and request.POST['NIT']:
            params['NIT'] = request.POST.get('NIT')
        response = requests.get(f'{FLASK_API_URL}/devolverEstadoCuenta', params=params)
        
        if response.status_code == 200:
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
        else:
            error = "Error al obtener los datos: " + response.text
    else:
        error = "Escriba un NIT o deje el campo vacío para obtener todos los datos."
        
    return render(request, 'EstadoCuenta.html', {'response': data, 'error': error})

def consultar_ingresos(request):
    ingresos = []
    graph = None
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        if fecha:
            params = {'fecha': fecha}
            response = requests.get(f'{FLASK_API_URL}/consultarIngresos', params=params)
            if response.status_code == 200:
                xml = ET.fromstring(response.content)
                for banco in xml.findall('banco'):
                    ingreso_data = {
                        'codigo': banco.find('codigo').text,
                        'nombre': banco.find('nombre').text,
                        'valor': banco.find('ingreso').text,
                        'fecha': banco.find('fecha').text
                    }
                    ingresos.append(ingreso_data)

                # Generar el gráfico aquí
                graph = generar_grafico(ingresos)
                context = {'graph': graph}
                return render(request, 'ingresos.html', context)
            else:
                return HttpResponse('Error en la solicitud al API de Flask', status=response.status_code)

    return render(request, 'ingresos.html', {'graph': None})

def generar_grafico(ingresos):
    # Estructura de datos para almacenar los ingresos organizados por banco y fecha
    datos_por_banco = defaultdict(lambda: defaultdict(float))
    for ingreso in ingresos:
        datos_por_banco[ingreso['nombre']][ingreso['fecha']] += float(ingreso['valor'])

    # Preparación de datos para el gráfico
    bancos = sorted(datos_por_banco.keys())
    fechas = sorted({fecha for datos in datos_por_banco.values() for fecha in datos})
    data = [ [datos_por_banco[banco][fecha] for fecha in fechas] for banco in bancos ] #

    if not fechas:
        return None # No hay datos para graficar

    # Asignación de colores por fecha
    colores = list(mcolors.TABLEAU_COLORS.values())  # Colores predefinidos de Matplotlib
    color_map = {fecha: colores[i % len(colores)] for i, fecha in enumerate(fechas)}

    # Configuración del gráfico
    fig, ax = plt.subplots(figsize=(10, 7))
    x = np.arange(len(bancos))
    width = 0.85 / len(fechas)  # Ancho de cada barra

    for i, fecha in enumerate(fechas):
        ax.bar(x - width/2 + i * width, [datos_por_banco[banco][fecha] for banco in bancos], width, label=fecha, color=color_map[fecha])

    ax.set_xlabel('Bancos')
    ax.set_ylabel('Miles de Quetzales')
    ax.set_title('Ingresos por Banco y Fecha')
    ax.set_xticks(x)
    ax.set_xticklabels(bancos)
    ax.legend(title='Fecha de Pago')

    plt.xticks(rotation=45)
    plt.tight_layout()

    # Guardar el gráfico en un buffer de bytes
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    
    return graph