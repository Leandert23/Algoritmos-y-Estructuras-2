# Main.py
"""
Punto de entrada principal del Simulador de Red LAN con CLI estilo router.
Inicializa la red con datos por defecto y ejecuta el bucle de comandos.
"""
from Red import Red
from CLI import CLI
from Errores import error_logger
from Arboles import AVLTree, BTree, Trie
from json import JSONEncoder, JSONDecoder

def inicializar_red_con_datos_por_defecto():
    """
    Inicializa la red con dispositivos, interfaces, rutas, políticas y snapshots por defecto para pruebas.
    """
    red = Red()

    # Agregar dispositivos
    red.agregar_dispositivo("router", "Router1")
    red.agregar_dispositivo("router", "Router2")
    red.agregar_dispositivo("switch", "Switch1")

    # Conectar dispositivos
    red.conectar("Router1", "Gi0/0", "Switch1", "Fa0/1")
    red.conectar("Router2", "Gi0/0", "Switch1", "Fa0/2")

    # Añadir interfaces manualmente (si no se agregaron automáticamente)
    red.obtener_dispositivo("Router1").agregar_interfaz("Gi0/0")
    red.obtener_dispositivo("Router1").agregar_interfaz("Gi0/1")
    red.obtener_dispositivo("Router2").agregar_interfaz("Gi0/0")
    red.obtener_dispositivo("Switch1").agregar_interfaz("Fa0/1")
    red.obtener_dispositivo("Switch1").agregar_interfaz("Fa0/2")

    # Asignar IPs y activar interfaces
    red.obtener_dispositivo("Router1").interfaces["Gi0/0"].ip = "192.168.1.1"
    red.obtener_dispositivo("Router1").interfaces["Gi0/0"].estado = True
    red.obtener_dispositivo("Router1").interfaces["Gi0/1"].ip = "10.0.0.1"
    red.obtener_dispositivo("Router1").interfaces["Gi0/1"].estado = True
    red.obtener_dispositivo("Router2").interfaces["Gi0/0"].ip = "192.168.2.1"
    red.obtener_dispositivo("Router2").interfaces["Gi0/0"].estado = True

    # Añadir rutas por defecto en las tablas AVL de los routers
    router1 = red.obtener_dispositivo("Router1")
    router1.tabla_rutas_avl.insertar("0.0.0.0", "0", "10.0.0.254", 10)  # Redacción simplificada: prefijo a 0.0.0.0
    router1.tabla_rutas_avl.insertar("192.168.2.0", "24", "192.168.1.254", 1)
    
    router2 = red.obtener_dispositivo("Router2")
    router2.tabla_rutas_avl.insertar("0.0.0.0", "0", "192.168.2.254", 10)
    router2.tabla_rutas_avl.insertar("10.0.0.0", "8", "192.168.2.1", 1)

    # Añadir políticas por defecto en los Tries de los routers
    router1.trie_politicas.insertar_prefijo("10.0.0.0", 8, {"ttl-min": 5})
    router1.trie_politicas.insertar_prefijo("192.168.0.0", 16, {"block": True})
    
    router2.trie_politicas.insertar_prefijo("192.168.2.0", 24, {"ttl-min": 3})

    # Añadir snapshots por defecto en el B-Tree global
    red.b_tree_snapshots.insertar("initial_config", "snap_00001.cfg")
    red.b_tree_snapshots.insertar("updated_config", "snap_00002.cfg")

    # Registrar algunos errores por defecto para pruebas
    error_logger.registrar_error("SyntaxError", "Comando de prueba inválido.", "test command")
    error_logger.registrar_error("ConnectionError", "Interfaz no encontrada por defecto.", "connect test")

    return red

def main():
    """
    Función principal: Inicializa la red, la CLI y ejecuta el bucle de comandos.
    """
    print("Bienvenido al Simulador de Red LAN estilo Router!")
    print("Escribe 'help' para ver comandos disponibles.")
    print("Escribe 'exit' para salir.\n")

    # Inicializar la red con datos por defecto
    red = inicializar_red_con_datos_por_defecto()
    cli = CLI(red)

    # Bucle principal de la CLI
    while True:
        prompt = cli.obtener_prompt()
        try:
            comando = input(prompt).strip()
            terminado, mensaje = cli.procesar_comando(comando)
            print(mensaje, end="")
            if terminado:
                break
        except KeyboardInterrupt:
            print("\n\n[Interrumpido por el usuario. Saliendo...] ")
            break
        except EOFError:
            print("\n\n[Fin de entrada. Saliendo...] ")
            break

if __name__ == "__main__":
    main()