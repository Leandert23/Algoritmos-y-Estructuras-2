class Interfaz:
    def __init__(self, nombre):
        self.nombre = nombre
        self.ip = None
        self.estado = False  
        self.conexiones = []  

    def conectar(self, dispositivo, interfaz):
        self.conexiones.append((dispositivo, interfaz))
    
    def desconectar(self, dispositivo, interfaz):
        self.conexiones.remove((dispositivo, interfaz))

class Dispositivo:
    def __init__(self, nombre, tipo):
        self.nombre = nombre
        self.tipo = tipo
        self.interfaces = {}
        self.estado = True  
        self.historial = []  
        self.cola_paquetes = []  

    def agregar_interfaz(self, nombre):
        if nombre not in self.interfaces:
            self.interfaces[nombre] = Interfaz(nombre)
            return True
        return False

class Router(Dispositivo):
    def __init__(self, nombre):
        super().__init__(nombre, "router")

class Switch(Dispositivo):
    def __init__(self, nombre):
        super().__init__(nombre, "switch")

class Host(Dispositivo):
    def __init__(self, nombre):
        super().__init__(nombre, "host")