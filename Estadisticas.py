class Estadisticas:
    def __init__(self, red):
        self.red = red
    
    def generar_reporte(self):
        return {
            'dispositivos': len(self.red.dispositivos),
            'paquetes_enviados': self.red.estadisticas['enviados'],
            'paquetes_entregados': self.red.estadisticas['entregados'],
            'tasa_entrega': (self.red.estadisticas['entregados'] / 
                            self.red.estadisticas['enviados'] * 100 
                            if self.red.estadisticas['enviados'] > 0 else 0)
        }

    def mostrar_historial(self, dispositivo):
        if dispositivo in self.red.dispositivos:
            return self.red.dispositivos[dispositivo].historial
        return []