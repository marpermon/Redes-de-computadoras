# Cantidad de bits
MAC = 8
IP = 8
Puerto = 16
AppCodigo = 2

class PC:
    APP_CODE = {
        "Telegram": 0,
        "WhatsApp": 1,
        "Facebook": 2,
    }
    
    # Se utilizará protocolo TCP para conexiones confiables

    APP_PORT = {
        "Telegram": 443,
        "WhatsApp": 443,
        "Facebook": 443,
    }

    def __init__(self, name, mac, ip):
        """
        Inicializacion objeto PC
        name: 'PC#'
        mac_int: entero 0..255 
        ip: entero 0..255 
        """
        self.name = name
        self.mac = mac
        self.ip = ip

    # --- helpers de serialización ---
    @staticmethod
    def _to_bits(n, width):
        return format(n, f'0{width}b')

    @staticmethod
    def _ascii_bits(s):
        return ''.join(format(ord(ch), '08b') for ch in s)

    # --- capas ---
    def capa_aplicacion(self, app_name, mensaje):
        app_code = self.APP_CODE[app_name]
        payload = f"{app_code},{mensaje}"
        print(f"Capa 5 (Aplicación): {payload}")
        return payload

    def capa_transporte(self, app_name, payload):
        port = self.APP_PORT[app_name]
        payload_t4 = f"{port},{payload}"
        print(f"Capa 4 (Transporte): {payload_t4}")
        return payload_t4

    def capa_red(self, dst_pc, payload_t4):
        payload_t3 = f"{self.ip},{dst_pc.ip},{payload_t4}"
        print(f"Capa 3 (Red): {payload_t3}")
        return payload_t3

    def capa_enlace(self, dst_pc, payload_t3):
        payload_t2 = f"{self.self.mac},{self.dst_pc.mac},{payload_t3}"
        print(f"Capa 2 (Enlace de Datos): {payload_t2}")
        return payload_t2

    def capa_fisica(self, payload_t4, enviar):
        if enviar:
            self_mac, dst_pc_mac, self_ip, dst_pc_ip, port, app_code, mensaje = payload_t4.split(',')
            bits = ""
            bits = bits + self._to_bits(self_mac, MAC)         # MAC src 8b
            bits = bits + self._to_bits(dst_pc_mac, MAC)       # MAC dst 8b
            bits = bits + self._to_bits(self_ip, IP)           # IP src 8b
            bits = bits + self._to_bits(dst_pc_ip, IP)         # IP dst 8b
            bits = bits + self._to_bits(port, Puerto)          # Puerto 16b
            bits = bits + self._to_bits(app_code, AppCodigo)   # AppCodigo 16b
            payload_ascii = f"{mensaje}"
            bits = bits + self._ascii_bits(payload_ascii)      # ASCII
            print(f"Capa 1 (Física): {bits}")
            return bits

    # --- flujo completo ---
    def enviar(self, dst_pc, app_name, mensaje):
        print("Iniciando encapsulamiento.")
        # Capa 5
        payload_app = self.capa_aplicacion(app_name, mensaje)
        # Capa 4
        payload_t4 = self.capa_transporte(app_name, payload_app)
        # Capa 3
        payload_t3 = self.capa_red(dst_pc, payload_t4)
        # Capa 2
        payload_t2 = self.capa_enlace(dst_pc, payload_t3)
        # Capa 1
        bitstream = self.capa_fisica(payload_t2)

        # Regresa numero binario formato string
        return bitstream
