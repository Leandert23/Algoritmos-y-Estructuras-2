# Dispositivos.py
from Arboles import AVLTree, Trie # Importar las nuevas estructuras de árboles

class Interfaz:
    """Representa una interfaz de red en un dispositivo."""
    def __init__(self, nombre):
        self.nombre = nombre
        self.ip = None
        self.estado = False  # False = shutdown (inactiva), True = no shutdown (activa)
        self.conexiones = [] # Lista de tuplas (nombre_dispositivo_remoto, nombre_interfaz_remota)

    def conectar(self, dispositivo_remoto_nombre, interfaz_remota_nombre):
        """Añade una conexión a esta interfaz."""
        if (dispositivo_remoto_nombre, interfaz_remota_nombre) not in self.conexiones:
            self.conexiones.append((dispositivo_remoto_nombre, interfaz_remota_nombre))
    
    def desconectar(self, dispositivo_remoto_nombre, interfaz_remota_nombre):
        """Elimina una conexión de esta interfaz."""
        if (dispositivo_remoto_nombre, interfaz_remota_nombre) in self.conexiones:
            self.conexiones.remove((dispositivo_remoto_nombre, interfaz_remota_nombre))

class Dispositivo:
    """Clase base para todos los dispositivos de red."""
    def __init__(self, nombre, tipo):
        self.nombre = nombre
        self.tipo = tipo
        self.interfaces = {} # Diccionario de interfaces por nombre
        self.estado = True  # True = encendido, False = apagado
        self.historial = []  # Para logs de actividad específicos del dispositivo
        self.cola_paquetes = [] # Cola de paquetes pendientes para procesamiento

    def agregar_interfaz(self, nombre):
        """Agrega una nueva interfaz al dispositivo si no existe."""
        if nombre not in self.interfaces:
            self.interfaces[nombre] = Interfaz(nombre)
            return True
        return False

    def obtener_interfaz(self, nombre):
        """Retorna un objeto Interfaz por su nombre."""
        return self.interfaces.get(nombre)

class Router(Dispositivo):
    """Representa un dispositivo Router."""
    def __init__(self, nombre):
        super().__init__(nombre, "router")
        self.tabla_rutas_avl = AVLTree() # Módulo 1: Tabla de enrutamiento con AVL
        self.trie_politicas = Trie()     # Módulo 3: Trie para prefijos IP y políticas
        # self.bst_arp = BST() # Placeholder: Si se implementa un BST para ARP

class Switch(Dispositivo):
    """Representa un dispositivo Switch."""
    def __init__(self, nombre):
        super().__init__(nombre, "switch")
        # self.tabla_mac = {} # Podría tener una tabla MAC

class Host(Dispositivo):
    """Representa un dispositivo Host (ej. PC)."""
    def __init__(self, nombre):
        super().__init__(nombre, "host")
        # self.tabla_arp = {} # Podría tener una tabla ARP simple