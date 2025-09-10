# CLI.py
from Errores import error_logger # Importar el logger de errores
import re # Para validación de IP y máscara
from Dispositivos import Router, Switch, Host

class CLI:
    """
    Clase que maneja la interfaz de línea de comandos (CLI) del simulador.
    Procesa los comandos del usuario y coordina las operaciones con la red.
    """
    def __init__(self, red):
        self.red = red # Referencia al objeto Red principal
        self.contexto = { # Estado actual de la CLI
            "modo": "usuario", # "usuario", "privilegiado", "configuracion", "interfaz"
            "dispositivo": None, # Nombre del dispositivo actualmente seleccionado
            "interfaz_actual": None # Nombre de la interfaz actualmente configurada
        }

    def obtener_prompt(self):
        """Retorna el prompt de la CLI según el modo actual."""
        base = self.contexto["dispositivo"] or ""
        if self.contexto["modo"] == "configuracion":
            return f"{base}(config)# "
        elif self.contexto["modo"] == "interfaz":
            return f"{base}(config-if)# "
        elif self.contexto["modo"] == "privilegiado":
            return f"{base}# "
        return f"{base}> "

    def _mostrar_banner(self, titulo):
        """Genera un banner formateado para la salida de la CLI."""
        return "\n" + "="*60 + "\n" + titulo.center(60) + "\n" + "="*60

    def procesar_comando(self, comando):
        """
        Procesa un comando ingresado por el usuario.
        Args:
            comando (str): El comando completo ingresado.
        Returns:
            tuple: (bool, str) - Éxito de la operación y mensaje de salida.
        """
        partes = comando.strip().split()
        if not partes:
            return False, ""

        cmd = partes[0].lower()
        args = partes[1:]

        # Manejo del comando 'exit' globalmente para todos los modos
        if cmd == "exit":
            if self.contexto["modo"] == "usuario":
                return True, self._mostrar_banner("SESIÓN TERMINADA") + "\n"
            else:
                # Volver al modo anterior
                if self.contexto["modo"] == "interfaz":
                    self.contexto["modo"] = "configuracion"
                    self.contexto["interfaz_actual"] = None
                    return False, "\nRegresando a modo configuración\n"
                elif self.contexto["modo"] == "configuracion":
                    self.contexto["modo"] = "privilegiado"
                    return False, "\nRegresando a modo privilegiado\n"
                elif self.contexto["modo"] == "privilegiado":
                    self.contexto["modo"] = "usuario"
                    self.contexto["dispositivo"] = None # Desconectar del dispositivo
                    return False, "\nRegresando a modo usuario\n"
        
        # Manejo del comando 'end' globalmente para salir a modo privilegiado
        if cmd == "end":
            if self.contexto["modo"] in ["configuracion", "interfaz"]:
                self.contexto["modo"] = "privilegiado"
                self.contexto["interfaz_actual"] = None
                return False, "\nRegresando a modo privilegiado\n"
            else:
                error_logger.registrar_error("SyntaxError", "Comando 'end' solo válido en modo configuración o interfaz.", comando)
                return False, "Error: 'end' solo es válido en modo configuración o interfaz."

        if cmd == "help":
            return self._mostrar_ayuda()

        # Delegar el procesamiento del comando según el modo actual
        if self.contexto["modo"] == "usuario":
            return self._procesar_modo_usuario(cmd, args, comando)
        elif self.contexto["modo"] == "privilegiado":
            return self._procesar_modo_privilegiado(cmd, args, comando)
        elif self.contexto["modo"] == "configuracion":
            return self._procesar_modo_configuracion(cmd, args, comando)
        elif self.contexto["modo"] == "interfaz":
            return self._procesar_modo_interfaz(cmd, args, comando)

        error_logger.registrar_error("CommandError", f"Modo CLI no reconocido: {self.contexto['modo']}", comando)
        return False, "Modo no reconocido"

    def _mostrar_ayuda(self):
        """Genera el mensaje de ayuda según el modo actual."""
        banner = self._mostrar_banner("AYUDA DEL SISTEMA")
        ayuda = ""
        if self.contexto["modo"] == "usuario":
            ayuda = """
Comandos disponibles:
  console <NOMBRE>   - Conectarse a un dispositivo
  enable             - Entrar en modo privilegiado
  listar             - Mostrar dispositivos disponibles
  help               - Mostrar esta ayuda
  exit               - Salir del simulador"""
        
        elif self.contexto["modo"] == "privilegiado":
            ayuda = """
Comandos disponibles:
  configure terminal - Entrar en modo configuración
  show interfaces    - Mostrar interfaces del dispositivo
  show ip route      - Mostrar tabla de rutas (AVL)
  show route avl-stats - Mostrar estadísticas AVL
  show ip route-tree - Mostrar árbol AVL
  show snapshots     - Mostrar snapshots de configuración (B-Tree)
  btree stats        - Mostrar estadísticas B-Tree
  show ip prefix-tree - Mostrar árbol de prefijos (Trie)
  show error-log [n] - Mostrar registro de errores
  send <origen> <destino_ip> <mensaje> - Enviar paquete (simulado)
  disable            - Volver a modo usuario
  help               - Mostrar esta ayuda
  exit               - Volver a modo usuario / Salir
  end                - Salir a modo privilegiado (si aplica)"""
        
        elif self.contexto["modo"] == "configuracion":
            ayuda = """
Comandos disponibles:
  interface <NOMBRE> - Configurar una interfaz
  hostname <NOMBRE>  - Cambiar nombre del dispositivo (en desarrollo)
  ip route add <prefix> <mask> via <next-hop> [metric N] - Añadir ruta AVL
  ip route del <prefix> <mask> - Eliminar ruta AVL
  policy set <prefix> <mask> ttl-min <N> - Establecer política TTL (Trie)
  policy set <prefix> <mask> block - Establecer política de bloqueo (Trie)
  policy unset <prefix> <mask> - Eliminar política (Trie)
  save snapshot <key> - Guardar configuración como snapshot (B-Tree)
  load config <key>  - Cargar configuración desde snapshot (B-Tree)
  exit               - Volver a modo privilegiado
  end                - Salir a modo privilegiado"""
        
        elif self.contexto["modo"] == "interfaz":
            ayuda = """
Comandos disponibles:
  ip address <IP>    - Asignar dirección IP
  shutdown           - Desactivar interfaz
  no shutdown        - Activar interfaz
  exit               - Volver a modo configuración
  end                - Salir a modo privilegiado"""

        return False, banner + ayuda + "\n" + "="*60 + "\n"

    def _procesar_modo_usuario(self, cmd, args, comando_completo):
        """Procesa comandos en modo usuario."""
        if cmd == "enable":
            if self.contexto["dispositivo"]:
                self.contexto["modo"] = "privilegiado"
                mensaje = self._mostrar_banner("MODO PRIVILEGIADO") + "\n"
                mensaje += "Advertencia: Ahora tiene acceso a comandos de configuración. Escriba 'help' para ver comandos.\n"
                return False, mensaje
            else:
                error_logger.registrar_error("CommandError", "Primero conéctese a un dispositivo (console <NOMBRE>)", comando_completo)
                return False, "Error: Primero conéctese a un dispositivo (console <NOMBRE>)"

        elif cmd == "console" and len(args) == 1:
            if args[0] in self.red.dispositivos:
                self.contexto["dispositivo"] = args[0]
                return False, f"\nConectado a {args[0]}\n"
            else:
                error_logger.registrar_error("ConnectionError", f"Dispositivo '{args[0]}' no encontrado", comando_completo)
                return False, f"\nError: Dispositivo '{args[0]}' no encontrado\n"

        elif cmd == "listar":
            dispositivos = "\n".join([
                f"  {nombre} ({disp.tipo})" 
                for nombre, disp in self.red.dispositivos.items()
            ])
            return False, self._mostrar_banner("DISPOSITIVOS DISPONIBLES") + "\n" + dispositivos + "\n"
        
        error_logger.registrar_error("SyntaxError", "Comando no válido en modo usuario.", comando_completo)
        return False, "Error: Comando no válido. Escriba 'help' para ayuda"

    def _procesar_modo_privilegiado(self, cmd, args, comando_completo):
        """Procesa comandos en modo privilegiado."""
        disp_nombre = self.contexto["dispositivo"]
        if not disp_nombre:
            error_logger.registrar_error("StateError", "Ningún dispositivo seleccionado en modo privilegiado.", comando_completo)
            return False, "Error: Ningún dispositivo seleccionado."
        
        dispositivo = self.red.obtener_dispositivo(disp_nombre)

        if cmd == "configure" and len(args) > 0 and args[0] == "terminal":
            self.contexto["modo"] = "configuracion"
            banner = self._mostrar_banner("MODO CONFIGURACIÓN GLOBAL")
            ayuda = """
Comandos disponibles:
  interface <NOMBRE> - Configurar interfaz específica
  hostname <NOMBRE>  - Cambiar nombre del dispositivo
  exit               - Volver a modo privilegiado"""
            return False, banner + ayuda + "\n" + "="*60 + "\n"

        elif cmd == "show":
            if len(args) > 0:
                if args[0] == "interfaces":
                    interfaces = []
                    for nombre, intf in dispositivo.interfaces.items():
                        estado = "ACTIVA" if intf.estado else "INACTIVA"
                        ip = intf.ip or "Sin dirección IP"
                        conexiones = "\n    ".join([f"{d}/{i}" for d, i in intf.conexiones])
                        
                        interfaz_info = [
                            f"Interfaz: {nombre}",
                            f"Estado: {estado}",
                            f"IP: {ip}",
                            "Conexiones:" + (f"\n    {conexiones}" if conexiones else " Ninguna")
                        ]
                        interfaces.append("\n".join(interfaz_info))
                    
                    banner = self._mostrar_banner(f"INTERFACES DE {disp_nombre}")
                    return False, banner + "\n\n" + "\n\n".join(interfaces) + "\n" + "="*60 + "\n"
                
                # --- Módulo 1: AVL (Tabla de Rutas) ---
                elif args[0] == "ip" and len(args) > 1 and args[1] == "route":
                    if isinstance(dispositivo, Router):
                        rutas = []
                        # Recorrido inorden del AVL para mostrar rutas
                        def _inorden_display(nodo):
                            if nodo:
                                _inorden_display(nodo.izquierda)
                                rutas.append(f"{nodo.prefix}/{nodo.mask} via {nodo.next_hop} metric {nodo.metric}")
                                _inorden_display(nodo.derecha)
                        dispositivo.tabla_rutas_avl._inorden_display = _inorden_display # Adjuntar para usar
                        dispositivo.tabla_rutas_avl._inorden_display(dispositivo.tabla_rutas_avl.raiz)
                        
                        return False, self._mostrar_banner(f"TABLA DE RUTAS DE {disp_nombre}") + "\n" + "\n".join(rutas) + "\nDefault: none\n"
                    error_logger.registrar_error("TypeError", "El dispositivo no es un router y no tiene tabla de rutas.", comando_completo)
                    return False, "Error: Este dispositivo no es un router."
                
                elif args[0] == "route" and len(args) > 1 and args[1] == "avl-stats":
                    if isinstance(dispositivo, Router):
                        stats = dispositivo.tabla_rutas_avl.obtener_stats()
                        return False, f"nodes={stats['nodos']} height={stats['altura']} rotations: LL={stats['rotaciones']['LL']} LR={stats['rotaciones']['LR']} RL={stats['rotaciones']['RL']} RR={stats['rotaciones']['RR']}\n"
                    error_logger.registrar_error("TypeError", "El dispositivo no es un router y no tiene estadísticas AVL.", comando_completo)
                    return False, "Error: Este dispositivo no es un router."

                elif args[0] == "ip" and len(args) > 1 and args[1] == "route-tree":
                    if isinstance(dispositivo, Router):
                        print(self._mostrar_banner(f"ÁRBOL AVL DE RUTAS DE {disp_nombre}"))
                        dispositivo.tabla_rutas_avl.imprimir_arbol_ascii()
                        return False, ""
                    error_logger.registrar_error("TypeError", "El dispositivo no es un router y no tiene árbol de rutas.", comando_completo)
                    return False, "Error: Este dispositivo no es un router."

                # --- Módulo 2: B-Tree (Snapshots) ---
                elif args[0] == "snapshots":
                    snapshots = self.red.b_tree_snapshots.recorrer_en_orden()
                    if snapshots:
                        output = "\n".join([f"{k} -> {v}" for k, v in snapshots]) # Asumiendo que recorrer_en_orden devuelve (key, value)
                        return False, self._mostrar_banner("SNAPSHOTS DE CONFIGURACIÓN") + "\n" + output + "\n"
                    return False, "No hay snapshots guardados.\n"
                
                # --- Módulo 3: Trie (Prefijos IP y Políticas) ---
                elif args[0] == "ip" and len(args) > 1 and args[1] == "prefix-tree":
                    if isinstance(dispositivo, Router):
                        print(self._mostrar_banner(f"ÁRBOL DE PREFIJOS IP Y POLÍTICAS DE {disp_nombre}"))
                        dispositivo.trie_politicas.imprimir_arbol_ascii()
                        return False, ""
                    error_logger.registrar_error("TypeError", "El dispositivo no es un router y no tiene árbol de prefijos.", comando_completo)
                    return False, "Error: Este dispositivo no es un router."

                # --- Módulo 4: Registro de Errores ---
                elif args[0] == "error-log":
                    cantidad = None
                    if len(args) > 1:
                        try:
                            cantidad = int(args[1])
                        except ValueError:
                            error_logger.registrar_error("SyntaxError", "Cantidad inválida para show error-log.", comando_completo)
                            return False, "Error: La cantidad debe ser un número entero."
                    
                    errores = error_logger.obtener_errores(cantidad)
                    if errores:
                        output = "\n".join([
                            f"[{e['timestamp']}] {e['tipo']}: {e['mensaje']} (Comando: {e['comando'] or 'N/A'})"
                            for e in errores
                        ])
                        return False, self._mostrar_banner("REGISTRO DE ERRORES") + "\n" + output + "\n"
                    return False, "No hay errores registrados.\n"

            error_logger.registrar_error("SyntaxError", "Comando 'show' incompleto o inválido.", comando_completo)
            return False, "Error: Comando 'show' no válido. Escriba 'help' para ayuda."

        elif cmd == "btree" and len(args) > 0 and args[0] == "stats":
            stats = self.red.b_tree_snapshots.obtener_stats()
            return False, f"order={stats['orden']} height={stats['altura']} nodes={stats['nodos']} splits={stats['splits']} merges={stats['merges']}\n"

        elif cmd == "send":
            if len(args) == 3:
                origen = args[0]
                destino_ip = args[1]
                mensaje = args[2]
                exito, msg = self.red.enviar_paquete(origen, destino_ip, mensaje)
                return False, msg
            error_logger.registrar_error("SyntaxError", "Uso: send <origen> <destino_ip> <mensaje>", comando_completo)
            return False, "Uso: send <origen> <destino_ip> <mensaje>"

        elif cmd == "disable":
            self.contexto["modo"] = "usuario"
            return False, "\nRegresando a modo usuario\n"

        error_logger.registrar_error("SyntaxError", "Comando no válido en modo privilegiado.", comando_completo)
        return False, "Error: Comando no válido. Escriba 'help' para ayuda"

    def _procesar_modo_configuracion(self, cmd, args, comando_completo):
        """Procesa comandos en modo configuración global."""
        disp_nombre = self.contexto["dispositivo"]
        dispositivo = self.red.obtener_dispositivo(disp_nombre)

        if cmd == "interface" and len(args) == 1:
            if not disp_nombre:
                error_logger.registrar_error("StateError", "Ningún dispositivo seleccionado.", comando_completo)
                return False, "Error: Ningún dispositivo seleccionado"
            
            if dispositivo.agregar_interfaz(args[0]):
                pass # Interfaz agregada si no existía
                
            self.contexto["modo"] = "interfaz"
            self.contexto["interfaz_actual"] = args[0]
            
            banner = self._mostrar_banner(f"CONFIGURANDO INTERFAZ {args[0]}")
            ayuda = """
Comandos disponibles:
  ip address <IP>    - Asignar dirección IP
  shutdown           - Desactivar interfaz
  no shutdown        - Activar interfaz
  exit               - Volver a modo configuración"""
            return False, banner + ayuda + "\n" + "="*60 + "\n"

        elif cmd == "hostname" and len(args) == 1:
            # Implementación de hostname (simplificada)
            dispositivo.nombre = args[0] # Cambia el nombre del objeto
            self.contexto["dispositivo"] = args[0] # Actualiza el contexto de la CLI
            return False, f"Nombre del dispositivo cambiado a {args[0]}\n"

        # --- Módulo 1: AVL (Comandos de Ruta) ---
        elif cmd == "ip" and len(args) >= 2 and args[0] == "route":
            if not isinstance(dispositivo, Router):
                error_logger.registrar_error("TypeError", "Este dispositivo no es un router y no soporta comandos 'ip route'.", comando_completo)
                return False, "Error: Este dispositivo no es un router."

            if args[1] == "add":
                # ip route add <prefix> <mask> via <next-hop> [metric N]
                if len(args) >= 7 and args[5] == "via":
                    prefix = args[3]
                    mask = args[4]
                    next_hop = args[6]
                    metric = 1 # Valor por defecto

                    # Validar IP y máscara (simplificado)
                    if not self._validar_ip(prefix) or not self._validar_ip(mask) or not self._validar_ip(next_hop):
                        error_logger.registrar_error("SyntaxError", "Formato de IP/máscara/next-hop inválido.", comando_completo)
                        return False, "Error: Formato de IP/máscara/next-hop inválido."

                    if len(args) >= 9 and args[7] == "metric":
                        try:
                            metric = int(args[8])
                        except ValueError:
                            error_logger.registrar_error("SyntaxError", "Métrica debe ser un número entero.", comando_completo)
                            return False, "Error: Métrica debe ser un número entero."

                    dispositivo.tabla_rutas_avl.insertar(prefix, mask, next_hop, metric)
                    return False, f"Ruta {prefix}/{mask} via {next_hop} metric {metric} añadida.\n"
                error_logger.registrar_error("SyntaxError", "Uso: ip route add <prefix> <mask> via <next-hop> [metric N]", comando_completo)
                return False, "Uso: ip route add <prefix> <mask> via <next-hop> [metric N]"
            
            elif args[1] == "del":
                # ip route del <prefix> <mask>
                if len(args) == 4:
                    prefix = args[2]
                    mask = args[3]
                    
                    if not self._validar_ip(prefix) or not self._validar_ip(mask):
                        error_logger.registrar_error("SyntaxError", "Formato de IP/máscara inválido.", comando_completo)
                        return False, "Error: Formato de IP/máscara inválido."

                    dispositivo.tabla_rutas_avl.eliminar(prefix, mask)
                    return False, f"Ruta {prefix}/{mask} eliminada (si existía).\n"
                error_logger.registrar_error("SyntaxError", "Uso: ip route del <prefix> <mask>", comando_completo)
                return False, "Uso: ip route del <prefix> <mask>"
            
            error_logger.registrar_error("SyntaxError", "Comando 'ip route' no válido.", comando_completo)
            return False, "Error: Comando 'ip route' no válido."

        # --- Módulo 3: Trie (Comandos de Política) ---
        elif cmd == "policy" and len(args) >= 2:
            if not isinstance(dispositivo, Router):
                error_logger.registrar_error("TypeError", "Este dispositivo no es un router y no soporta comandos 'policy'.", comando_completo)
                return False, "Error: Este dispositivo no es un router."

            if args[0] == "set":
                # policy set <prefix> <mask> ttl-min <N>
                # policy set <prefix> <mask> block
                if len(args) >= 4:
                    prefix = args[1]
                    mask = args[2]
                    
                    if not self._validar_ip(prefix) or not self._validar_ip(mask):
                        error_logger.registrar_error("SyntaxError", "Formato de IP/máscara inválido.", comando_completo)
                        return False, "Error: Formato de IP/máscara inválido."

                    mask_length = self._mask_to_cidr(mask)
                    if mask_length is None:
                        error_logger.registrar_error("SyntaxError", "Máscara de subred inválida.", comando_completo)
                        return False, "Error: Máscara de subred inválida."

                    politicas = {}
                    if args[3] == "ttl-min" and len(args) == 5:
                        try:
                            ttl = int(args[4])
                            politicas['ttl-min'] = ttl
                            dispositivo.trie_politicas.insertar_prefijo(prefix, mask_length, politicas)
                            return False, f"Política TTL mínimo {ttl} establecida para {prefix}/{mask}.\n"
                        except ValueError:
                            error_logger.registrar_error("SyntaxError", "TTL mínimo debe ser un número entero.", comando_completo)
                            return False, "Error: TTL mínimo debe ser un número entero."
                    elif args[3] == "block" and len(args) == 4:
                        politicas['block'] = True
                        dispositivo.trie_politicas.insertar_prefijo(prefix, mask_length, politicas)
                        return False, f"Política de bloqueo establecida para {prefix}/{mask}.\n"
                error_logger.registrar_error("SyntaxError", "Uso: policy set <prefix> <mask> ttl-min <N> | block", comando_completo)
                return False, "Uso: policy set <prefix> <mask> ttl-min <N> | block"
            
            elif args[0] == "unset":
                # policy unset <prefix> <mask>
                if len(args) == 3:
                    prefix = args[1]
                    mask = args[2]
                    
                    if not self._validar_ip(prefix) or not self._validar_ip(mask):
                        error_logger.registrar_error("SyntaxError", "Formato de IP/máscara inválido.", comando_completo)
                        return False, "Error: Formato de IP/máscara inválido."

                    mask_length = self._mask_to_cidr(mask)
                    if mask_length is None:
                        error_logger.registrar_error("SyntaxError", "Máscara de subred inválida.", comando_completo)
                        return False, "Error: Máscara de subred inválida."

                    dispositivo.trie_politicas.eliminar_prefijo(prefix, mask_length) # Esto solo desmarca el fin de prefijo
                    return False, f"Política para {prefix}/{mask} eliminada (si existía).\n"
                error_logger.registrar_error("SyntaxError", "Uso: policy unset <prefix> <mask>", comando_completo)
                return False, "Uso: policy unset <prefix> <mask>"
            
            error_logger.registrar_error("SyntaxError", "Comando 'policy' no válido.", comando_completo)
            return False, "Error: Comando 'policy' no válido."

        # --- Módulo 2: B-Tree (Comandos de Snapshot) ---
        elif cmd == "save" and len(args) >= 2 and args[0] == "snapshot":
            # save snapshot <key>
            key = args[1]
            # En un sistema real, aquí se guardaría la configuración actual a un archivo
            # y se obtendría un puntero/nombre de archivo.
            # Por ahora, solo se simula el guardado y se indexa.
            file_name = f"snap_{len(self.red.b_tree_snapshots.recorrer_en_orden()) + 1:05d}.cfg"
            self.red.b_tree_snapshots.insertar(key, file_name)
            return False, f"[OK] snapshot {key} -> file: {file_name} (indexed)\n"

        elif cmd == "load" and len(args) >= 2 and args[0] == "config":
            # load config <key>
            key = args[1]
            file_name = self.red.b_tree_snapshots.buscar(key)
            if file_name:
                # Aquí se cargaría la configuración desde el archivo
                return False, f"[OK] Configuración cargada desde {file_name} (key: {key}).\n"
            error_logger.registrar_error("ConfigError", f"Snapshot con clave '{key}' no encontrado.", comando_completo)
            return False, f"Error: Snapshot con clave '{key}' no encontrado.\n"

        error_logger.registrar_error("SyntaxError", "Comando no válido en modo configuración.", comando_completo)
        return False, "Error: Comando no válido. Escriba 'help' para ayuda"

    def _procesar_modo_interfaz(self, cmd, args, comando_completo):
        """Procesa comandos en modo configuración de interfaz."""
        if not self.contexto["dispositivo"] or not self.contexto["interfaz_actual"]:
            error_logger.registrar_error("StateError", "Interfaz no seleccionada.", comando_completo)
            return False, "Error: Interfaz no seleccionada"
        
        disp = self.red.dispositivos[self.contexto["dispositivo"]]
        intf = disp.interfaces[self.contexto["interfaz_actual"]]

        if cmd == "ip" and len(args) >= 2 and args[0] == "address":
            ip_address = args[1]
            if not self._validar_ip(ip_address):
                error_logger.registrar_error("SyntaxError", "Formato de dirección IP inválido.", comando_completo)
                return False, "Error: Formato de dirección IP inválido."
            
            intf.ip = ip_address
            intf.estado = True # Asume que al asignar IP, la interfaz se activa
            return False, f"\nDirección IP {ip_address} asignada a {self.contexto['interfaz_actual']}\n"

        elif cmd == "shutdown":
            intf.estado = False
            return False, f"\nInterfaz {self.contexto['interfaz_actual']} DESACTIVADA (shutdown)\n"

        elif cmd == "no" and len(args) == 1 and args[0] == "shutdown":
            intf.estado = True
            return False, f"\nInterfaz {self.contexto['interfaz_actual']} ACTIVADA (no shutdown)\n"

        error_logger.registrar_error("SyntaxError", "Comando no válido en modo interfaz.", comando_completo)
        return False, "Error: Comando no válido. Escriba 'help' para ayuda"

    # --- Funciones de utilidad para validación ---
    def _validar_ip(self, ip_str):
        """Valida si una cadena es una dirección IP válida (IPv4 simple)."""
        pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        if re.match(pattern, ip_str):
            parts = list(map(int, ip_str.split('.')))
            return all(0 <= part <= 255 for part in parts)
        return False

    def _mask_to_cidr(self, mask_str):
        """Convierte una máscara de subred (ej. 255.255.255.0) a longitud CIDR (ej. 24)."""
        try:
            octets = list(map(int, mask_str.split('.')))
            if len(octets) != 4 or not all(0 <= o <= 255 for o in octets):
                return None
            
            binary_mask = ''.join(f'{octet:08b}' for octet in octets)
            # Una máscara válida debe tener solo unos seguidos de solo ceros
            if '01' in binary_mask:
                return None
            
            return binary_mask.count('1')
        except ValueError:
            return None