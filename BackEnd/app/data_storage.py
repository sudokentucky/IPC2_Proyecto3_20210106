from models.Cliente import Cliente
from models.Banco import Banco 
from models.Factura import Factura
from models.Pago import Pago
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta
import re

class GestorXML:
    def __init__(self):
        self.clientes = []
        self.bancos = []
        self.facturas = []
        self.pagos = []


    def cargar_configuracion(self, archivo_xml):
        root = ET.fromstring(archivo_xml)
        creados_clientes, actualizados_clientes = 0, 0
        creados_bancos, actualizados_bancos = 0, 0

        for elem in root.findall('./clientes/cliente'):
            NIT, nombre = elem.find('NIT').text, elem.find('nombre').text
            # Extraer solo el valor alfanumérico del NIT, ignorando "NIT:", "nit:", "NIT=" y "nit=" si están presentes
            NIT = re.search(r'\b(?:NIT:|nit:|NIT=|nit=)?([A-Za-z0-9]+-[A-Za-z0-9]+)\b', NIT)
            if NIT:
                NIT = NIT.group(1)  # Usar el grupo 1 para obtener solo el NIT, sin "NIT:", "nit:", "NIT=" o "nit="
            else:
                continue  # Si no se encuentra un NIT válido, saltar a la siguiente iteración
            if self.agregar_cliente(NIT, nombre):
                creados_clientes += 1
            else:
                actualizados_clientes += 1

        for elem in root.findall('./bancos/banco'):
            codigo, nombre = elem.find('codigo').text, elem.find('nombre').text
            if self.agregar_banco(codigo, nombre):
                creados_bancos += 1
            else:
                actualizados_bancos += 1

        return creados_clientes, actualizados_clientes, creados_bancos, actualizados_bancos

    def cargar_transacciones(self, archivo_xml):
        pagos_unicos = set() # Conjunto para almacenar pagos únicos y evitar duplicados
        root = ET.fromstring(archivo_xml)
        nuevas_facturas, facturas_duplicadas, facturas_con_error = 0, 0, 0
        nuevos_pagos, pagos_duplicados, pagos_con_error = 0, 0, 0

        for elem in root.findall('./facturas/factura'):
            numeroFactura = elem.find('numeroFactura').text
            NITcliente = elem.find('NITcliente').text
            fecha = elem.find('fecha').text
            valor = elem.find('valor').text

            # Extraer solo el valor alfanumérico del NIT, ignorando "NIT:", "nit:", "NIT=" y "nit=" si están presentes
            NITcliente = re.search(r'\b(?:NIT:|nit:|NIT=|nit=)?([A-Za-z0-9]+-[A-Za-z0-9]+)\b', NITcliente)
            numeroFactura = re.search(r'\b[A-Za-z0-9]+\b', numeroFactura)
            fecha = re.search(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', fecha)
            valor = re.search(r'\b\d+(\.\d+)?\b', valor)

            #verificar si hay facturas duplicadas, con error y nuevas
            if NITcliente and numeroFactura and fecha and valor:
                NITcliente = NITcliente.group(1)
                numeroFactura = numeroFactura.group(0)
                fecha = fecha.group(0)
                valor = float(valor.group(0))

                # Crear una tupla con los campos únicos de la factura
                factura_unico = (numeroFactura, NITcliente, fecha)

                # Verificar si la factura ya está en el set de facturas únicas
                if factura_unico in pagos_unicos:
                    facturas_duplicadas += 1
                else:
                    pagos_unicos.add(factura_unico)
                    if self.agregar_factura(numeroFactura, NITcliente, fecha, valor):
                        nuevas_facturas += 1
            else:
                facturas_con_error += 1

        for elem in root.findall('./pagos/pago'):
            codigoBanco = elem.find('codigoBanco').text
            fecha = elem.find('fecha').text
            NITcliente = elem.find('NITcliente').text
            valor = elem.find('valor').text

            # Extraer solo el valor alfanumérico del NIT, ignorando "NIT:", "nit:", "NIT=" y "nit=" si están presentes
            NITcliente = re.search(r'\b(?:NIT:|nit:|NIT=|nit=)?([A-Za-z0-9]+-[A-Za-z0-9]+)\b', NITcliente)
            fecha = re.search(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', fecha)
            valor = re.search(r'\b(?:Q\.)?(\d+(\.\d+)?)(?:\s*quetzales)?\b', valor, re.IGNORECASE)

            if NITcliente and fecha and valor:
                NITcliente = NITcliente.group(1)
                fecha = fecha.group(0)
                valor = float(valor.group(1))

                # Crear una tupla con los campos únicos del pago
                pago_unico = (codigoBanco, NITcliente, fecha)

                # Verificar si el pago ya está en el set de pagos únicos
                if pago_unico in pagos_unicos:
                    pagos_duplicados += 1
                else:
                    pagos_unicos.add(pago_unico)
                    if self.agregar_pago(codigoBanco, fecha, NITcliente, valor):
                        nuevos_pagos += 1
            else:
                pagos_con_error += 1

        return nuevas_facturas, facturas_duplicadas, facturas_con_error, nuevos_pagos, pagos_duplicados, pagos_con_error

    def agregar_cliente(self, NIT, nombre):
        for cliente in self.clientes:
            if cliente.NIT == NIT:
                if cliente.nombre != nombre:
                    cliente.nombre = nombre
                    return False  # Retornar False indica que fue una actualización
                return False  # Ningún cambio necesario, pero el NIT ya existía
        nuevo_cliente = Cliente(NIT, nombre)
        self.clientes.append(nuevo_cliente)
        # imprimir listas
        for cliente in self.clientes:
            print(cliente.NIT)
            print(cliente.nombre)
        for banco in self.bancos:
            print(banco.codigo)
            print(banco.nombre)
            print("________________________")
        return True  # Verdadero indica que se creó un nuevo cliente


    def agregar_banco(self, codigo, nombre):
        # Agregar o actualizar banco
        for banco in self.bancos:
            if banco.codigo == codigo:
                banco.nombre = nombre
                return False
        self.bancos.append(Banco(codigo, nombre))
        return True
    
    def limpiarDatos(self):
        # Limpiar datos
        self.__init__()
    
    def get_ingresos(self, NIT=None):
        #devuelve los ingresos totales para un mes especifico
        ingresos = 0
        for factura in self.facturas:
            if NIT is None or factura.NITcliente == NIT:
                ingresos += factura.valor
        return ingresos
    
    def consultar_estado_cuenta(self, NIT=None):
        clientes_ordenados = sorted(self.clientes, key=lambda c: c.NIT)
        resultados = []

        for cliente in clientes_ordenados:
            if NIT is None or cliente.NIT == NIT:
                saldo = 0
                transacciones = []

                # Facturas (consideradas como cargos)
                for factura in self.facturas:
                    if factura.NITcliente == cliente.NIT:
                        saldo += factura.valor
                        transacciones.append((factura.fecha, f'Factura # {factura.numeroFactura}', factura.valor))

                # Pagos (considerados como abonos)
                for pago in self.pagos:
                    if pago.NITcliente == cliente.NIT:
                        # Buscar el banco correspondiente al pago
                        banco = next((b for b in self.bancos if b.codigo == pago.codigoBanco), None)
                        nombre_banco = banco.nombre if banco else 'Desconocido'
                        saldo -= pago.valor
                        transacciones.append((pago.fecha, f'Pago ({nombre_banco})', -pago.valor))

                # Ordenar transacciones por fecha
                transacciones.sort(key=lambda x: x[0], reverse=True)
                
                resultados.append((cliente, saldo, transacciones))
                if NIT is not None:
                    break  # Si se especificó un NIT, terminar después del primer cliente

        return resultados

    def agregar_factura(self, numeroFactura, NITcliente, fecha, valor):
        # Agregar factura si no existe
        for factura in self.facturas:
            if factura.numeroFactura == numeroFactura:
                return False  # Ya existe
        self.facturas.append(Factura(numeroFactura, NITcliente, fecha, valor))
        return True

    def agregar_pago(self, codigoBanco, fecha, NITcliente, valor):
        # Agregar pago si no existe
        for pago in self.pagos:
            if pago.codigoBanco == codigoBanco and pago.NITcliente == NITcliente and pago.fecha == fecha:
                return False  # Ya existe
        self.pagos.append(Pago(codigoBanco, fecha, NITcliente, valor))
        return True

    def consultar_ingresos(self, fecha):
        # Convertir la fecha de entrada para obtener el primer día del mes especificado
        mes, año = map(int, fecha.split('/'))
        # Crear un objeto datetime para el primer día del mes dado
        fecha = datetime(year=año, month=mes, day=1)
        
        # Calcular la fecha tres meses antes
        fecha_inicio = fecha - timedelta(days=90)

        ingresos = {}

        # Recorrer todos los pagos
        for pago in self.pagos:
            try:
                # Convertir la fecha del pago a un objeto datetime
                fecha_pago = datetime.strptime(pago.fecha, '%d/%m/%Y')
            except ValueError as e:
                # Manejo de errores si el formato no es correcto
                print(f"Error en el formato de fecha: {e}")
                continue

            # Verificar si el pago está dentro del rango de fechas
            if fecha_inicio <= fecha_pago < fecha:
                # Buscar el banco correspondiente al pago
                banco = next((b for b in self.bancos if b.codigo == pago.codigoBanco), None)
                nombre_banco = banco.nombre if banco else 'Desconocido'
                if pago.codigoBanco not in ingresos: 
                    ingresos[pago.codigoBanco] = {'valor': 0, 'nombre_banco': nombre_banco, 'fecha': pago.fecha}
                ingresos[pago.codigoBanco]['valor'] += pago.valor 

        # Convertir los ingresos a miles de quetzales
        for banco in ingresos:
            ingresos[banco]['valor']
        return ingresos

