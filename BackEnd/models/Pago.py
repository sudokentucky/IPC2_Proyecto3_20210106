class Pago:
    def __init__(self, codigoBanco, fecha, NITcliente, valor):
        self.codigoBanco = codigoBanco
        self.fecha = fecha
        self.NITcliente = NITcliente
        self.valor = valor

    def __str__(self):
        return f'Pago({self.codigoBanco}, {self.fecha}, {self.NITcliente}, {self.valor})'
    