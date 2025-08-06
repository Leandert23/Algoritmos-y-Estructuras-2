import json

def guardar_config(red, archivo):
    config = {
        "dispositivos": [],
        "conexiones": []
    }
    
    for nombre, disp in red.dispositivos.items():
        dispositivo = {
            "nombre": nombre,
            "tipo": disp.tipo,
            "interfaces": []
        }
        for intf in disp.interfaces.values():
            dispositivo["interfaces"].append({
                "nombre": intf.nombre,
                "ip": intf.ip,
                "estado": intf.estado
            })
        config["dispositivos"].append(dispositivo)
    
    with open(archivo, 'w') as f:
        json.dump(config, f, indent=2)
    return True

def cargar_config(red, archivo):
    try:
        with open(archivo, 'r') as f:
            config = json.load(f)
        
        red.dispositivos.clear()
        
        for disp in config["dispositivos"]:
            red.agregar_dispositivo(disp["tipo"], disp["nombre"])
            for intf in disp["interfaces"]:
                red.dispositivos[disp["nombre"]].agregar_interfaz(intf["nombre"])
                red.dispositivos[disp["nombre"]].interfaces[intf["nombre"]].ip = intf["ip"]
                red.dispositivos[disp["nombre"]].interfaces[intf["nombre"]].estado = intf["estado"]
        
        return True
    except Exception as e:
        print(f"Error al cargar: {str(e)}")
        return False