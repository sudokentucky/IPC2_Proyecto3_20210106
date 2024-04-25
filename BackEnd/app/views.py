# app/views.py
from flask import Response, Blueprint, request, make_response
from .data_storage import GestorXML
from datetime import datetime
from flask import jsonify
from xml.etree.ElementTree import Element, SubElement, tostring


bp = Blueprint('api', __name__, url_prefix='/api')

# Crear una instancia de DataStore
data_store = GestorXML()

@bp.route('/grabarConfiguracion', methods=['POST'])
def cargar_configuracion():
    xml_string = request.data.decode('utf-8')
    creados_clientes, actualizados_clientes, creados_bancos, actualizados_bancos = data_store.cargar_configuracion(xml_string)

    # Generar respuesta XML
    respuesta = Element('respuesta')

    clientes = SubElement(respuesta, 'clientes')
    creados_clientes_elem = SubElement(clientes, 'creados')
    creados_clientes_elem.text = str(creados_clientes)
    actualizados_clientes_elem = SubElement(clientes, 'actualizados')
    actualizados_clientes_elem.text = str(actualizados_clientes)

    bancos = SubElement(respuesta, 'bancos')
    creados_bancos_elem = SubElement(bancos, 'creados')
    creados_bancos_elem.text = str(creados_bancos)
    actualizados_bancos_elem = SubElement(bancos, 'actualizados')
    actualizados_bancos_elem.text = str(actualizados_bancos)

    # Convertir el objeto Element a una cadena
    respuesta_xml = tostring(respuesta, encoding='utf-8').decode('utf-8')

    # Devolver la respuesta XML directamente
    return Response(respuesta_xml, mimetype='application/xml')
    

@bp.route('/grabarTransaccion', methods=['POST'])
def cargar_transaccion():
    xml_string = request.data.decode('utf-8')
    nuevas_facturas, facturas_duplicadas, facturas_con_error, nuevos_pagos, pagos_duplicados, pagos_con_error = data_store.cargar_transacciones(xml_string)

    # Crear el elemento raíz
    transacciones = Element('transacciones')

    # Agregar elementos de factura
    facturas = SubElement(transacciones, 'facturas')
    SubElement(facturas, 'nuevasFacturas').text = str(nuevas_facturas)
    SubElement(facturas, 'facturasDuplicadas').text = str(facturas_duplicadas)
    SubElement(facturas, 'facturasConError').text = str(facturas_con_error)

    # Agregar elementos de pago
    pagos = SubElement(transacciones, 'pagos')
    SubElement(pagos, 'nuevosPagos').text = str(nuevos_pagos)
    SubElement(pagos, 'pagosDuplicados').text = str(pagos_duplicados)
    SubElement(pagos, 'pagosConError').text = str(pagos_con_error)

    # Convertir el objeto Element a una cadena XML
    respuesta_xml = tostring(transacciones, encoding='utf-8').decode('utf-8')

    # Devolver la respuesta XML directamente con el correcto MIME type
    return Response(respuesta_xml, mimetype='application/xml')

@bp.route('/limpiarDatos', methods=['GET'])
def limpiar():
    try:
        data_store.limpiarDatos()
        return make_response(jsonify(message="Datos eliminados correctamente"), 204)
    except Exception as e:
        return make_response(jsonify(message="Error al borrar los datos: " + str(e)), 500)

@bp.route('/devolverEstadoCuenta', methods=['GET'])
def devolver_estado_cuenta():
    NIT = request.args.get('NIT')
    resultados = data_store.consultar_estado_cuenta(NIT)

    # Convertir los resultados a XML
    respuesta_xml = '''<?xml version="1.0"?>
<clientes>'''
    for cliente, saldo, transacciones in resultados:
        respuesta_xml += f'''
<cliente>
<NIT>{cliente.NIT}</NIT>
<nombre>{cliente.nombre}</nombre>
<saldo>{saldo}</saldo>
<transacciones>'''
        for fecha, descripcion, valor,  in transacciones:
            respuesta_xml += f'''
<transaccion>
<fecha>{fecha}</fecha>
<descripcion>{descripcion}</descripcion>
<valor>{valor}</valor>
</transaccion>'''
        respuesta_xml += '''
</transacciones>
</cliente>'''
    respuesta_xml += '''
</clientes>'''

    response = make_response(respuesta_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

@bp.route('/consultarIngresos', methods=['GET'])
def consultar_ingresos():
    fecha = request.args.get('fecha')  # Obtiene la fecha como una cadena 'mm/yyyy'
    if not validar_fecha_mm_yyyy(fecha):
        return jsonify({"error": "Formato de fecha incorrecto. Utilice el formato MM/YYYY"}), 400

    ingresos = data_store.consultar_ingresos(fecha)  # Pasa la fecha directamente

    # Generar respuesta JSON
    respuesta_json = []
    for banco, ingreso in ingresos.items():
        respuesta_json.append({
            'banco': {
                'codigo': banco,
                'nombre': ingreso['nombre_banco'],
                'ingreso': ingreso['valor'],
                'fecha': ingreso['fecha']
            }
        })

    return jsonify(respuesta_json)

def validar_fecha_mm_yyyy(fecha):
    try:
        datetime.strptime(fecha, '%m/%Y')
        return True
    except ValueError:
        return False