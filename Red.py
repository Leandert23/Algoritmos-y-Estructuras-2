class Interfaz:
    def __init__(self, nombre):
        self.nombre = nombre
        self.ip = None
        self.estado = False  
        self.conexiones = []

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

class Red:
    def __init__(self):
        self.dispositivos = {}
    
    def agregar_dispositivo(self, tipo, nombre):
        if nombre in self.dispositivos:
            return False
        
        if tipo.lower() == "router":
            self.dispositivos[nombre] = Router(nombre)
        elif tipo.lower() == "switch":
            self.dispositivos[nombre] = Switch(nombre)
        else:
            self.dispositivos[nombre] = Host(nombre)
        return True
    
    def conectar(self, disp1, int1, disp2, int2):
        if (disp1 in self.dispositivos and disp2 in self.dispositivos and
            int1 in self.dispositivos[disp1].interfaces and
            int2 in self.dispositivos[disp2].interfaces):
            
            self.dispositivos[disp1].interfaces[int1].conexiones.append((disp2, int2))
            self.dispositivos[disp2].interfaces[int2].conexiones.append((disp1, int1))
            return True
        return False