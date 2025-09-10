# Errores.py
from datetime import datetime
from Estructuras import Cola

class RegistroErrores:
    """Clase para gestionar el registro cronológico de errores del simulador."""
    def __init__(self):
        self.cola_errores = Cola()

    def registrar_error(self, tipo_error, mensaje, comando_provocador=None):
        """
        Registra un nuevo error en la cola.
        
        Args:
            tipo_error (str): Categoría del error (ej. "SyntaxError", "ConnectionError").
            mensaje (str): Descripción detallada del problema.
            comando_provocador (str, optional): El comando que causó el error. Defaults to None.
        """
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "tipo": tipo_error,
            "mensaje": mensaje,
            "comando": comando_provocador
        }
        self.cola_errores.encolar(error_info)
        # Opcional: imprimir en consola para feedback inmediato
        # print(f"ERROR REGISTRADO: [{error_info['timestamp']}] {tipo_error} - {mensaje}")

    def obtener_errores(self, cantidad=None):
        """
        Retorna una lista de errores registrados.
        
        Args:
            cantidad (int, optional): Número máximo de errores recientes a retornar.
                                      Si es None, retorna todos. Defaults to None.
        Returns:
            list: Lista de diccionarios, cada uno representando un error.
        """
        # Se obtienen los errores más recientes si se especifica una cantidad
        if cantidad is not None and cantidad > 0:
            return self.cola_errores.items[-cantidad:]
        return self.cola_errores.items

    def limpiar_errores(self):
        """Limpia todos los errores del registro."""
        self.cola_errores = Cola()
        print("Registro de errores limpiado.")

# Instancia global para el registro de errores, accesible desde cualquier parte del código.
error_logger = RegistroErrores()