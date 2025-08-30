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

    def __init__(self, name, mac_int, ip_last_octet):
        """
        name: 'PC1' o 'PC2'
        mac_int: entero pequeño (p.ej. 7 para '07')
        ip_last_octet: entero 0..255 (p.ej. 110)
        """
        self.name = name
        self.mac = mac_int
        self.ip_last = ip_last_octet

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
        payload = f"{app_code} {mensaje}"
        texto = f"Capa 5 (Aplicación): {payload}"
        return app_code, payload, texto

    def capa_transporte(self, app_name, payload):
        port = self.APP_PORT[app_name]
        payload_t4 = f"{port} {payload}"
        texto = f"Capa 4 (Transporte): {payload_t4}"
        return port, payload_t4, texto

    def capa_red(self, dst_pc, port, payload_t4):
        # Para el texto mostramos últimos octetos (simplificación)
        payload_t3 = f"{self.ip_last} {dst_pc.ip_last} {payload_t4}"
        texto = f"Capa 3 (Red): {self.ip_last} {dst_pc.ip_last} {payload_t4}"
        return payload_t3, texto

    def capa_enlace(self, dst_pc, payload_t3):
        # Para el texto usamos MACs en enteros cortos (src dst ...)
        payload_t2 = f"{self._fmt_mac(self.mac)} {self._fmt_mac(dst_pc.mac)} {payload_t3}"
        texto = f"Capa 2 (Enlace de Datos): {payload_t2}"
        return payload_t2, texto

    def capa_fisica(self, dst_pc, port, app_code, mensaje):
        """
        Serializa a bits con el patrón de tu salida:
        - MAC src: 8 bits
        - MAC dst: 16 bits
        - IP src: 8 bits
        - IP dst: 8 bits
        - Puerto: 16 bits
        - Payload (app_code + ' ' + mensaje): ASCII
        """
        bits = []
        bits.append(self._to_bits(self.mac, 8))           # MAC src 8b
        bits.append(self._to_bits(dst_pc.mac, 16))        # MAC dst 16b (para calzar tu ejemplo)
        bits.append(self._to_bits(self.ip_last, 8))       # IP src 8b
        bits.append(self._to_bits(dst_pc.ip_last, 8))     # IP dst 8b
        bits.append(self._to_bits(port, 16))              # Puerto 16b
        payload_ascii = f"{app_code} {mensaje}"
        bits.append(self._ascii_bits(payload_ascii))      # ASCII
        bitstream = ''.join(bits)
        texto = f"Capa 1 (Física): {bitstream}"
        return bitstream, texto

    @staticmethod
    def _fmt_mac(mac_int):
        # Mostrar con cero a la izquierda si es <10, para lucir como '07'
        return f"{mac_int:02d}"

    # --- flujo completo ---
    def enviar(self, dst_pc, app_name, mensaje, imprimir=True):
        # Capa 5
        app_code, payload_app, t5 = self.capa_aplicacion(app_name, mensaje)
        # Capa 4
        port, payload_t4, t4 = self.capa_transporte(app_name, payload_app)
        # Capa 3
        payload_t3, t3 = self.capa_red(dst_pc, port, payload_t4)
        # Capa 2
        payload_t2, t2 = self.capa_enlace(dst_pc, payload_t3)
        # Capa 1
        bitstream, t1 = self.capa_fisica(dst_pc, port, app_code, mensaje)

        if imprimir:
            print("Iniciando encapsulamiento.")
            print(t5)
            print(t4)
            print(t3)
            print(t2)
            print(t1)

        # Regresa todo por si lo quieres usar en tests
        return {
            "app": t5,
            "transporte": t4,
            "red": t3,
            "enlace": t2,
            "fisica": t1,
            "bitstream": bitstream
        }


# --- Ejemplo de uso que reproduce tu salida ---
if __name__ == "__main__":
    pc1 = PC("PC1", mac_int=7, ip_last_octet=110)
    pc2 = PC("PC2", mac_int=3, ip_last_octet=100)
    # App = "Facebook", mensaje = "Hola"
    pc1.enviar(pc2, "Facebook", "Hola", imprimir=True)
