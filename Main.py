from Red import Red
from CLI import CLI

def mostrar_ayuda(modo):
    print("\n" + "="*50)
    if modo == "usuario":
        print("MODO USUARIO (>):".center(50))
        print("- console <NOMBRE> - Conectarse a dispositivo")
        print("- enable           - Modo privilegio")
        print("- listar           - Mostrar dispositivos")
    else:
        print("MODO PRIVILEGIADO (#):".center(50))
        print("- configure terminal - Modo configuración")
        print("- show interfaces    - Ver interfaces")
        print("- disable            - Volver a modo usuario")
    print("- exit              - Salir")
    print("="*50)

def main():
    red = Red()
    red.agregar_dispositivo("router", "R1")
    red.agregar_dispositivo("host", "PC1")
    red.dispositivos["R1"].agregar_interfaz("g0/0")
    red.dispositivos["PC1"].agregar_interfaz("eth0")
    red.conectar("R1", "g0/0", "PC1", "eth0")

    cli = CLI(red)
    print("\n¡Bienvenido al Simulador de Red LAN!")
    print("Escribe 'menu' para ver comandos o 'exit' para salir\n")

    while True:
        try:
            prompt = cli.obtener_prompt()
            comando = input(prompt).strip()
            if not comando:
                continue
                
            if comando.lower() == "menu":
                mostrar_ayuda(cli.contexto["modo"])
                continue
                
            if comando.lower() == "exit":
                print("\nSesión terminada\n")
                break
                
            if comando.lower() == "listar":
                print("\nDISPOSITIVOS DISPONIBLES (usar NOMBRES EXACTOS):")
                print("- R1 (router)")
                print("- PC1 (host)\n")
                continue
                
            exito, mensaje = cli.procesar_comando(comando)
            if mensaje:
                print(mensaje)
                
        except KeyboardInterrupt:
            print("\nUse 'exit' para salir\n")
        except Exception as e:
            print(f"\nError: {str(e)}")
main()