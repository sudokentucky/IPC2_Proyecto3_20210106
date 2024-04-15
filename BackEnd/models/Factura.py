class Factura:
    def __init__(self, numeroFactura, NITcliente, fecha, valor):
        self.numeroFactura = numeroFactura
        self.NITcliente = NITcliente
        self.fecha = fecha
        self.valor = valor

    def __str__(self):
        return f'Factura({self.numeroFactura}, {self.NITcliente}, {self.fecha}, {self.valor})'
    