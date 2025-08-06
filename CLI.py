class CLI:
    def __init__(self, red):
        self.red = red
        self.contexto = {
            "modo": "usuario",
            "dispositivo": None,
            "interfaz_actual": None
        }

    def obtener_prompt(self):
        base = self.contexto["dispositivo"] or ""
        if self.contexto["modo"] == "configuracion":
            return f"{base}(config)# "
        elif self.contexto["modo"] == "interfaz":
            return f"{base}(config-if)# "
        elif self.contexto["modo"] == "privilegiado":
            return f"{base}# "
        return f"{base}> "

    def _mostrar_banner(self, titulo):
        return "\n" + "="*60 + "\n" + titulo.center(60) + "\n" + "="*60

    def procesar_comando(self, comando):
        partes = comando.strip().split()
        if not partes:
            return False, ""

        cmd = partes[0].lower()
        args = partes[1:]

        if cmd == "exit":
            return True, self._mostrar_banner("SESIÓN TERMINADA") + "\n"

        if cmd == "help":
            return self._mostrar_ayuda()

        if self.contexto["modo"] == "usuario":
            return self._procesar_modo_usuario(cmd, args)

        elif self.contexto["modo"] == "privilegiado":
            return self._procesar_modo_privilegiado(cmd, args)

        elif self.contexto["modo"] == "configuracion":
            return self._procesar_modo_configuracion(cmd, args)

        elif self.contexto["modo"] == "interfaz":
            return self._procesar_modo_interfaz(cmd, args)

        return False, "Modo no reconocido"

    def _mostrar_ayuda(self):
        banner = self._mostrar_banner("AYUDA DEL SISTEMA")
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
  send <origen> <destino> <mensaje> - Enviar paquete
  disable            - Volver a modo usuario
  help               - Mostrar esta ayuda
  exit               - Salir del simulador"""
        
        elif self.contexto["modo"] == "configuracion":
            ayuda = """
Comandos disponibles:
  interface <NOMBRE> - Configurar una interfaz
  hostname <NOMBRE>  - Cambiar nombre del dispositivo
  exit               - Volver a modo privilegiado
  end                - Salir a modo privilegiado"""
        
        else:
            ayuda = """
Comandos disponibles:
  ip address <IP>    - Asignar dirección IP
  shutdown           - Desactivar interfaz
  no shutdown        - Activar interfaz
  exit               - Volver a modo configuración
  end                - Salir a modo privilegiado"""

        return False, banner + ayuda + "\n" + "="*60 + "\n"

    def _procesar_modo_usuario(self, cmd, args):
        if cmd == "enable":
            if self.contexto["dispositivo"]:
                self.contexto["modo"] = "privilegiado"
                mensaje = self._mostrar_banner("MODO PRIVILEGIADO") + "\n"
                mensaje += "Advertencia: Ahora tiene acceso a comandos de configuración. escriba 'menu'\n"
                return True, mensaje
            return False, "Error: Primero conéctese a un dispositivo (console <NOMBRE>)"

        elif cmd == "console" and len(args) == 1:
            if args[0] in self.red.dispositivos:
                self.contexto["dispositivo"] = args[0]
                return True, f"\nConectado a {args[0]}\n"
            return False, f"\nError: Dispositivo '{args[0]}' no encontrado\n"

        elif cmd == "listar":
            dispositivos = "\n".join([
                f"  {nombre} ({disp.tipo})" 
                for nombre, disp in self.red.dispositivos.items()
            ])
            return False, self._mostrar_banner("DISPOSITIVOS DISPONIBLES") + "\n" + dispositivos + "\n"

        return False, "Error: Comando no válido. Escriba 'help' para ayuda"

    def _procesar_modo_privilegiado(self, cmd, args):
        if cmd == "configure" and len(args) > 0 and args[0] == "terminal":
            self.contexto["modo"] = "configuracion"
            banner = self._mostrar_banner("MODO CONFIGURACIÓN GLOBAL")
            ayuda = """
Comandos disponibles:
  interface <NOMBRE> - Configurar interfaz específica
  hostname <NOMBRE>  - Cambiar nombre del dispositivo
  exit               - Volver a modo privilegiado"""
            return True, banner + ayuda + "\n" + "="*60 + "\n"

        elif cmd == "show" and len(args) > 0 and args[0] == "interfaces":
            if not self.contexto["dispositivo"]:
                return False, "Error: Ningún dispositivo seleccionado"
            
            disp = self.red.dispositivos[self.contexto["dispositivo"]]
            interfaces = []
            
            for nombre, intf in disp.interfaces.items():
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
            
            banner = self._mostrar_banner(f"INTERFACES DE {self.contexto['dispositivo']}")
            return True, banner + "\n\n" + "\n\n".join(interfaces) + "\n" + "="*60 + "\n"

        elif cmd == "disable":
            self.contexto["modo"] = "usuario"
            return True, "\nRegresando a modo usuario\n"

        return False, "Error: Comando no válido. Escriba 'help' para ayuda"

    def _procesar_modo_configuracion(self, cmd, args):
        if cmd == "interface" and len(args) == 1:
            if not self.contexto["dispositivo"]:
                return False, "Error: Ningún dispositivo seleccionado"
            
            disp = self.red.dispositivos[self.contexto["dispositivo"]]
            if args[0] not in disp.interfaces:
                disp.agregar_interfaz(args[0])
                
            self.contexto["modo"] = "interfaz"
            self.contexto["interfaz_actual"] = args[0]
            
            banner = self._mostrar_banner(f"CONFIGURANDO INTERFAZ {args[0]}")
            ayuda = """
Comandos disponibles:
  ip address <IP>    - Asignar dirección IP
  shutdown           - Desactivar interfaz
  no shutdown        - Activar interfaz
  exit               - Volver a modo configuración"""
            return True, banner + ayuda + "\n" + "="*60 + "\n"

        elif cmd == "hostname" and len(args) == 1:
            
            return False, "Comando en desarrollo: hostname"

        elif cmd in ["exit", "end"]:
            self.contexto["modo"] = "privilegiado"
            return True, "\nRegresando a modo privilegiado\n"

        return False, "Error: Comando no válido. Escriba 'help' para ayuda"

    def _procesar_modo_interfaz(self, cmd, args):
        if not self.contexto["dispositivo"] or not self.contexto["interfaz_actual"]:
            return False, "Error: Interfaz no seleccionada"
        
        disp = self.red.dispositivos[self.contexto["dispositivo"]]
        intf = disp.interfaces[self.contexto["interfaz_actual"]]

        if cmd == "ip" and len(args) >= 2 and args[0] == "address":
            intf.ip = args[1]
            return True, f"\nDirección IP {args[1]} asignada a {self.contexto['interfaz_actual']}\n"

        elif cmd == "shutdown":
            intf.estado = False
            return True, f"\nInterfaz {self.contexto['interfaz_actual']} DESACTIVADA (shutdown)\n"

        elif cmd == "no" and len(args) == 1 and args[0] == "shutdown":
            intf.estado = True
            return True, f"\nInterfaz {self.contexto['interfaz_actual']} ACTIVADA (no shutdown)\n"

        elif cmd in ["exit", "end"]:
            modo_anterior = "privilegiado" if cmd == "end" else "configuracion"
            self.contexto["modo"] = modo_anterior
            self.contexto["interfaz_actual"] = None
            return True, f"\nRegresando a modo {modo_anterior}\n"

        return False, "Error: Comando no válido. Escriba 'help' para ayuda"