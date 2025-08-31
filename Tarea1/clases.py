class PC:
    APP_CODE = {
        "Telegram": "9",
        "WhatsApp": "10",
        "Facebook": "11",
    }
    APP_PORT = {
        "Telegram": 443,
        "WhatsApp": 443,
        "Facebook": 443,
    }

    def __init__(self, name, mac_int, ip):
        """
        Inicializacion objeto PC
        name: 'PC#'
        mac_int: entero 0..255 
        ip: entero 0..255 
        """
        self.name = name
        self.mac = mac_int
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
        # Para el texto mostramos últimos octetos (simplificación)
        payload_t3 = f"{self.ip},{dst_pc.ip},{payload_t4}"
        print(f"Capa 3 (Red): {payload_t3}")
        return payload_t3

    def capa_enlace(self, dst_pc, payload_t3):
        # Para el texto usamos MACs en enteros cortos (src dst ...)
        payload_t2 = f"{self._fmt_mac(self.mac)},{self._fmt_mac(dst_pc.mac)},{payload_t3}"
        print(f"Capa 2 (Enlace de Datos): {payload_t2}")
        return payload_t2

    def capa_fisica(self, payload_t4):
        """
        Serializa a bits:
        - MAC src: 8 bits
        - MAC dst: 8 bits
        - IP src: 8 bits
        - IP dst: 8 bits
        - Puerto: 16 bits
        - Payload (app_code + ' ' + mensaje): ASCII
        """
        self_mac, dst_pc_mac, self_ip, dst_pc_ip, port, app_code, mensaje = payload_t4.split(',')
        bits = []
        bits.append(self._to_bits(self_mac, 8))           # MAC src 8b
        bits.append(self._to_bits(dst_pc_mac, 8))        # MAC dst 8b
        bits.append(self._to_bits(self_ip, 8))       # IP src 8b
        bits.append(self._to_bits(dst_pc_ip, 8))     # IP dst 8b
        bits.append(self._to_bits(port, 16))              # Puerto 16b
        payload_ascii = f"{app_code} {mensaje}"
        bits.append(self._ascii_bits(payload_ascii))      # ASCII
        bitstream = ''.join(bits)
        print(f"Capa 1 (Física): {bitstream}")
        return bitstream

    @staticmethod
    def _fmt_mac(mac_int):
        # Mostrar con cero a la izquierda si es <10, para lucir como '07'
        return f"{mac_int:02d}"

    # --- flujo completo ---
    def enviar(self, dst_pc, app_name, mensaje, imprimir=True):
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
        bitstream = self.capa_fisica(dst_pc, mensaje)

        # Regresa numero binario
        return bitstream
