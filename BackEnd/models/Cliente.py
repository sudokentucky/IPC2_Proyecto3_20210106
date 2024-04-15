

class Cliente:
    def __init__(self, NIT, nombre):
        if not NIT or not nombre:
            raise ValueError("NIT y nombre son requeridos")
        self._NIT = NIT
        self._nombre = nombre

    @property
    def NIT(self):
        return self._NIT

    @NIT.setter
    def NIT(self, value):
        if not value:
            raise ValueError("NIT no puede estar vacío")
        self._NIT = value

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        if not value:
            raise ValueError("Nombre no puede estar vacío")
        self._nombre = value

    def __str__(self):
        return f"Cliente {self._NIT}: {self._nombre}"