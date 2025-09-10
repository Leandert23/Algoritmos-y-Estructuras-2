# Red.py
from Dispositivos import Router, Switch, Host, Interfaz # Importar clases de dispositivos
from Arboles import BTree # Importar el B-Tree para snapshots
from Errores import error_logger # Importar el logger de errores

class Red:
    """
    Clase principal que gestiona todos los dispositivos de la red,
    sus conexiones y el índice de snapshots de configuración.
    """
    def __init__(self):
        self.dispositivos = {} # Diccionario de dispositivos {nombre: objeto_dispositivo}
        self.b_tree_snapshots = BTree(t=4) # Módulo 2: B-Tree para snapshots (grado mínimo t=4 como ejemplo)
        self.estadisticas = { # Estadísticas generales de la red
            'paquetes_enviados': 0,
            'paquetes_entregados': 0
        }
    
    def agregar_dispositivo(self, tipo, nombre):
        """
        Agrega un nuevo dispositivo a la red.
        Args:
            tipo (str): Tipo de dispositivo ("router", "switch", "host").
            nombre (str): Nombre único del dispositivo.
        Returns:
            bool: True si se agregó, False si ya existe o el tipo es inválido.
        """
        if nombre in self.dispositivos:
            error_logger.registrar_error("ConfigError", f"El dispositivo '{nombre}' ya existe en la red.", comando_provocador=f"agregar_dispositivo {tipo} {nombre}")
            return False
        
        if tipo.lower() == "router":
            self.dispositivos[nombre] = Router(nombre)
        elif tipo.lower() == "switch":
            self.dispositivos[nombre] = Switch(nombre)
        elif tipo.lower() == "host":
            self.dispositivos[nombre] = Host(nombre)
        else:
            error_logger.registrar_error("ConfigError", f"Tipo de dispositivo inválido: '{tipo}'.", comando_provocador=f"agregar_dispositivo {tipo} {nombre}")
            return False # Tipo de dispositivo no válido
        return True
    
    def obtener_dispositivo(self, nombre):
        """Retorna un objeto dispositivo por su nombre."""
        return self.dispositivos.get(nombre)

    def conectar(self, disp1_nombre, int1_nombre, disp2_nombre, int2_nombre):
        """
        Establece una conexión bidireccional entre dos interfaces de dispositivos.
        Args:
            disp1_nombre (str): Nombre del primer dispositivo.
            int1_nombre (str): Nombre de la interfaz del primer dispositivo.
            disp2_nombre (str): Nombre del segundo dispositivo.
            int2_nombre (str): Nombre de la interfaz del segundo dispositivo.
        Returns:
            tuple: (bool, str) - Éxito de la operación y mensaje.
        """
        disp1 = self.obtener_dispositivo(disp1_nombre)
        disp2 = self.obtener_dispositivo(disp2_nombre)

        if not disp1 or not disp2:
            error_logger.registrar_error("ConnectionError", f"Uno o ambos dispositivos no existen: {disp1_nombre}, {disp2_nombre}.", comando_provocador=f"conectar {disp1_nombre} {int1_nombre} {disp2_nombre} {int2_nombre}")
            return False, "Error: Uno o ambos dispositivos no existen."

        int1 = disp1.obtener_interfaz(int1_nombre)
        int2 = disp2.obtener_interfaz(int2_nombre)

        if not int1 or not int2:
            error_logger.registrar_error("ConnectionError", f"Una o ambas interfaces no existen: {int1_nombre} en {disp1_nombre} o {int2_nombre} en {disp2_nombre}.", comando_provocador=f"conectar {disp1_nombre} {int1_nombre} {disp2_nombre} {int2_nombre}")
            return False, "Error: Una o ambas interfaces no existen."
        
        # Conexión bidireccional
        int1.conectar(disp2_nombre, int2_nombre)
        int2.conectar(disp1_nombre, int1_nombre)
        return True, f"Conexión establecida entre {disp1_nombre}:{int1_nombre} y {disp2_nombre}:{int2_nombre}"

    def desconectar(self, disp1_nombre, int1_nombre, disp2_nombre, int2_nombre):
        """
        Elimina una conexión bidireccional entre dos interfaces de dispositivos.
        Args:
            disp1_nombre (str): Nombre del primer dispositivo.
            int1_nombre (str): Nombre de la interfaz del primer dispositivo.
            disp2_nombre (str): Nombre del segundo dispositivo.
            int2_nombre (str): Nombre de la interfaz del segundo dispositivo.
        Returns:
            tuple: (bool, str) - Éxito de la operación y mensaje.
        """
        disp1 = self.obtener_dispositivo(disp1_nombre)
        disp2 = self.obtener_dispositivo(disp2_nombre)

        if not disp1 or not disp2:
            error_logger.registrar_error("ConnectionError", f"Uno o ambos dispositivos no existen: {disp1_nombre}, {disp2_nombre}.", comando_provocador=f"desconectar {disp1_nombre} {int1_nombre} {disp2_nombre} {int2_nombre}")
            return False, "Error: Uno o ambos dispositivos no existen."

        int1 = disp1.obtener_interfaz(int1_nombre)
        int2 = disp2.obtener_interfaz(int2_nombre)

        if not int1 or not int2:
            error_logger.registrar_error("ConnectionError", f"Una o ambas interfaces no existen: {int1_nombre} en {disp1_nombre} o {int2_nombre} en {disp2_nombre}.", comando_provocador=f"desconectar {disp1_nombre} {int1_nombre} {disp2_nombre} {int2_nombre}")
            return False, "Error: Una o ambas interfaces no existen."
        
        # Desconexión bidireccional
        int1.desconectar(disp2_nombre, int2_nombre)
        int2.desconectar(disp1_nombre, int1_nombre)
        return True, f"Desconexión realizada entre {disp1_nombre}:{int1_nombre} y {disp2_nombre}:{int2_nombre}"

    def enviar_paquete(self, origen_nombre, destino_ip, mensaje):
        """
        Simula el envío de un paquete a través de la red.
        Este método implementa el flujo de procesamiento de paquetes:
        Trie (políticas) -> AVL (rutas) -> (ARP/siguiente salto).
        
        Args:
            origen_nombre (str): Nombre del dispositivo de origen.
            destino_ip (str): Dirección IP de destino del paquete.
            mensaje (str): Contenido del mensaje del paquete.
        Returns:
            tuple: (bool, str) - Éxito de la operación y mensaje de resultado.
        """
        self.estadisticas['paquetes_enviados'] += 1
        
        origen_disp = self.obtener_dispositivo(origen_nombre)
        if not origen_disp:
            error_logger.registrar_error("PacketError", f"Dispositivo de origen '{origen_nombre}' no encontrado.", comando_provocador=f"send {origen_nombre} {destino_ip} {mensaje}")
            return False, f"Error: Dispositivo de origen '{origen_nombre}' no encontrado."

        print(f"\n--- Iniciando envío de paquete desde {origen_nombre} a {destino_ip} ---")

        # Paso 1: Consulta de Políticas en el Trie (si es un Router)
        if isinstance(origen_disp, Router):
            print(f"[{origen_nombre}] Consultando políticas en Trie para {destino_ip}...")
            politicas = origen_disp.trie_politicas.obtener_politica(destino_ip)
            if 'block' in politicas and politicas['block']:
                error_logger.registrar_error("PacketBlocked", f"Paquete bloqueado por política en {origen_nombre} para {destino_ip}.", comando_provocador=f"send {origen_nombre} {destino_ip} {mensaje}")
                print(f"[{origen_disp.nombre}] Paquete BLOQUEADO por política para {destino_ip}.")
                return False, f"Paquete bloqueado por política en {origen_nombre} para {destino_ip}."
            
            if 'ttl-min' in politicas:
                print(f"[{origen_disp.nombre}] Política 'ttl-min' de {politicas['ttl-min']} aplicada.")
            # Aquí se aplicarían otras políticas si existieran

        # Paso 2: Consulta de Ruta en el AVL (si es un Router)
        next_hop = None
        if isinstance(origen_disp, Router):
            print(f"[{origen_nombre}] Consultando tabla de rutas (AVL) para {destino_ip}...")
            ruta_encontrada = origen_disp.tabla_rutas_avl.buscar(destino_ip) # Esto es una búsqueda simplificada
            
            if ruta_encontrada:
                next_hop = ruta_encontrada.next_hop
                print(f"[{origen_nombre}] Ruta encontrada: Siguiente salto via {next_hop}.")
            else:
                error_logger.registrar_error("PacketDiscarded", f"No hay ruta conocida desde {origen_nombre} para {destino_ip}.", comando_provocador=f"send {origen_nombre} {destino_ip} {mensaje}")
                print(f"[{origen_nombre}] No hay ruta conocida para {destino_ip}. Paquete descartado.")
                return False, f"No hay ruta conocida desde {origen_nombre} para {destino_ip}. Paquete descartado."
        else: # Para Hosts o Switches, asume conexión directa o gateway
            print(f"[{origen_nombre}] Dispositivo no es un router. Asumiendo conexión directa o vía gateway.")
            next_hop = destino_ip # Asume que el destino es el siguiente salto directo para simplificar
            
        # Paso 3: Simulación de Reenvío al Siguiente Salto
        print(f"[{origen_nombre}] Paquete reenviado (simulado) hacia {next_hop}...")
        self.estadisticas['paquetes_entregados'] += 1 # Asume entrega exitosa por ahora
        print(f"--- Paquete enviado con éxito (simulado) a {destino_ip} ---")
        return True, f"Paquete enviado con éxito (simulado) a {destino_ip}."