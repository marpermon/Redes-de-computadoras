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
        return format(int(n), f'0{width}b')
    
    @staticmethod
    def _from_bits(bits):
        return int(bits, 2)

    @staticmethod
    def _ascii_bits(s):
        return ''.join(format(ord(ch), '08b') for ch in s)
    
    @staticmethod
    def _bits_ascii(bits):
        return ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))

    # --- capas ---
    def capa_aplicacion(self, data, enviar, app_name=None):
        if enviar:    
            app_code = self.APP_CODE[app_name]
            payload = f"{app_code},{data}"
            print(f"Capa 5 (Aplicación): {payload}")
            return payload
        
        else: # Recibe segmento de capa 3 para convertirlo en payload
            port, *resto = data.split(',')
            mensaje = ','.join(resto)
            print(f"Capa 5 (Aplicación) - Desempaquetado: {mensaje}")
            return mensaje 

    def capa_transporte(self, data, enviar, app_name=None):
        if enviar: # Recibe payload de capa 5 para convertirlo en segmento
            port = self.APP_PORT[app_name]
            segmento = f"{port},{data}"
            print(f"Capa 4 (Transporte): {segmento}")
            return segmento
    
        else: # Recibe segmento de capa 3 para convertirlo en payload
            port, *resto = data.split(',')
            payload = ','.join(resto)
            print(f"Capa 4 (Transporte) - Desempaquetado: {payload}")
            return payload 

    def capa_red(self, data, enviar, dst_pc=None):
        if enviar: # Recibe segmento de capa 4 para convertirlo en paquete
            paquete = f"{self.ip},{dst_pc.ip},{data}"
            print(f"Capa 3 (Red): {paquete}")
            return paquete
        
        else: # Recibe paquete de capa 2 para convertirlo en segmento
            origin_ip, dst_pc_ip, *resto = data.split(',')
            if int(dst_pc_ip) != self.ip:
                raise ValueError(f"La IP {dst_pc_ip} no coincide con la IP esperada {self.ip}.")
            segmento = ','.join(resto)
            print(f"Capa 3 (Red) - Desempaquetado: {segmento}")
            return segmento 

    def capa_enlace(self, data, enviar, dst_pc=None):
        if enviar:  # Recibe paquete de capa 3 para convertirlo en trama
            trama = f"{self.mac},{dst_pc.mac},{data}" 
            print(f"Capa 2 (Enlace de Datos): {trama}")
            return trama
        
        else: # Recibe trama de capa 1 para convertirla en paquete
            print(data.split(','))
            origin_mac, dst_pc_mac, *resto = data.split(',')
            if int(dst_pc_mac) != self.mac:
                raise ValueError(f"La MAC {dst_pc_mac} no coincide con la MAC esperada {self.mac}.")
            paquete = ','.join(resto)
            print(f"Capa 2 (Enlace de Datos) - Desempaquetado: {paquete}")
            return paquete         

    def capa_fisica(self, data, enviar):
        if enviar: # Recibe trama de capa 2 para convertirla en bits
            origin_mac, dst_pc_mac, origin_ip, dst_pc_ip, port, app_code, mensaje = data.split(',')
            data = ""
            data = data + self._to_bits(origin_mac, MAC)         # MAC src 8b
            data = data + self._to_bits(dst_pc_mac, MAC)       # MAC dst 8b
            data = data + self._to_bits(origin_ip, IP)           # IP src 8b
            data = data + self._to_bits(dst_pc_ip, IP)         # IP dst 8b
            data = data + self._to_bits(port, Puerto)          # Puerto 16b
            data = data + self._to_bits(app_code, AppCodigo)   # AppCodigo 16b
            payload_ascii = f"{mensaje}"
            data = data + self._ascii_bits(payload_ascii)      # ASCII
            print(f"Capa 1 (Física): {data}")
            return data
        
        else: # Manda bit como trama a capa 2
            origin_mac = self._from_bits(data[:MAC])           # 8b MAC origen
            dst_pc_mac = self._from_bits(data[MAC:MAC*2])  # 8b MAC destino
            origin_ip = self._from_bits(data[MAC*2:MAC*2+IP])  # 8b IP origen
            dst_pc_ip = self._from_bits(data[MAC*2+IP:MAC*2+IP*2])  # 8b IP destino
            port = self._from_bits(data[MAC*2+IP*2:MAC*2+IP*2+Puerto])  # 16b Puerto
            app_code = self._from_bits(data[MAC*2+IP*2+Puerto:MAC*2+IP*2+Puerto+AppCodigo])  # 16b Código App
            payload_bits = data[MAC*2+IP*2+Puerto+AppCodigo:]  # El resto son los datos del mensaje

            # Convertir el payload de bits ASCII a texto
            mensaje = self._bits_ascii(payload_bits)

            # Volver a construir la trama
            trama = f"{origin_mac},{dst_pc_mac},{origin_ip},{dst_pc_ip},{port},{app_code},{mensaje}"
            
            print(f"Capa 1 (Física) - Desempaquetado: {trama}")
            return trama

    # --- flujo completo ---
    def enviar(self, dst_pc, app_name, mensaje):
        print("Iniciando encapsulamiento.")
        # Capa 5
        payload_app = self.capa_aplicacion(mensaje, enviar = True, app_name=app_name)
        # Capa 4
        segmento = self.capa_transporte(payload_app, enviar = True, app_name=app_name)
        # Capa 3
        paquete = self.capa_red(segmento, enviar = True, dst_pc=dst_pc)
        # Capa 2
        trama = self.capa_enlace(paquete, enviar = True, dst_pc=dst_pc)
        # Capa 1
        bitstream = self.capa_fisica(trama, enviar = True)

        # Regresa numero binario formato string
        return bitstream

    def recibir(self, bitstream):
        print("Iniciando desencapsulamiento.")
        # Capa 1 (Física)
        trama = self.capa_fisica(bitstream, enviar=False)
        # Capa 2 (Enlace de datos)
        paquete = self.capa_enlace(trama, enviar=False)
        # Capa 3 (Red)
        segmento = self.capa_red(paquete, enviar=False)
        # Capa 4 (Transporte)
        payload_app = self.capa_transporte(segmento, enviar=False)
        # Capa 5 (Aplicación)
        mensaje = self.capa_aplicacion(payload_app, enviar=False)

        # Regresa el mensaje original
        return mensaje

# ------------------ Utilidades de red --------------------
def _b2i(b): return int(b, 2)
def _i2b(n, w): return format(int(n), f"0{w}b")

def parse_bitstream(bits_):
    """Extrae campos del bitstream (formato de PC.capa_fisica)."""
    off = 0
    src_mac = _b2i(bits_[off:off+MAC]); off += MAC
    dst_mac = _b2i(bits_[off:off+MAC]); off += MAC
    src_ip  = _b2i(bits_[off:off+IP]);  off += IP
    dst_ip  = _b2i(bits_[off:off+IP]);  off += IP
    port    = _b2i(bits_[off:off+Puerto]); off += Puerto
    app     = _b2i(bits_[off:off+AppCodigo]); off += AppCodigo
    payload_bits = bits_[off:]
    return src_mac, dst_mac, src_ip, dst_ip, port, app, payload_bits

def build_bitstream(src_mac, dst_mac, src_ip, dst_ip, port, app, payload_bits):
    return (_i2b(src_mac, MAC) + _i2b(dst_mac, MAC) + _i2b(src_ip, IP) + _i2b(dst_ip, IP) +
            _i2b(port, Puerto) + _i2b(app, AppCodigo) + payload_bits)

def rewrite_mac(bits_, new_src=None, new_dst=None):
    src_mac, dst_mac, src_ip, dst_ip, port, app, payload_bits = parse_bitstream(bits_)
    if new_src is None: new_src = src_mac
    if new_dst is None: new_dst = dst_mac
    return build_bitstream(new_src, new_dst, src_ip, dst_ip, port, app, payload_bits)

def bits_to_trama(bits_):
    src_mac, dst_mac, src_ip, dst_ip, port, app, payload_bits = parse_bitstream(bits_)
    # payload está en ASCII en bits
    mensaje = ''.join(chr(int(payload_bits[i:i+8], 2)) for i in range(0, len(payload_bits), 8))
    return f"{src_mac},{dst_mac},{src_ip},{dst_ip},{port},{app},{mensaje}"

def print_capas_desde_bits(bits_, titulo=None):
    if titulo: print(titulo)
    print(f"Capa 1 (Física): {bits_}")
    trama = bits_to_trama(bits_)
    print(f"Capa 2 (Enlace de Datos): {trama}")
    # Capa 3: quitar MACs
    _, _, src_ip, dst_ip, port, app, mensaje = trama.split(',', 6)
    print(f"Capa 3 (Red): {src_ip},{dst_ip},{port},{app},{mensaje}")
    # Capa 4: quitar IPs
    print(f"Capa 4 (Transporte): {port},{app},{mensaje}")
    # Capa 5: quitar puerto
    print(f"Capa 5 (Aplicación): {app},{mensaje}")

# ---------------------- Switch (L2) ----------------------
class Switch:
    """
    Conmutador capa 2 con aprendizaje MAC.
    forward(bits, puerto_entrada) -> (puerto_salida, bits)
    """
    def __init__(self, name):
        self.name = name
        self.mac_table = {}    # mac -> puerto

    def forward(self, bits_in, ingress_port, puertos_disponibles):
        src_mac, dst_mac, *_ = parse_bitstream(bits_in)
        # Aprendizaje de la MAC origen
        self.mac_table[src_mac] = ingress_port

        if dst_mac in self.mac_table:
            out_port = self.mac_table[dst_mac]
            if out_port == ingress_port:
                print(f"En {self.name}: destino está en el mismo puerto {ingress_port}, no reenvía.")
                return None, bits_in
            print(f"En {self.name}: entra por el puerto {ingress_port}")
            print(f"En {self.name}: sale por el puerto {out_port}")
            return out_port, bits_in
        else:
            # Flooding (elige el primer puerto distinto al de entrada)
            out_candidates = [p for p in puertos_disponibles if p != ingress_port]
            out_port = out_candidates[0] if out_candidates else None
            print(f"En {self.name}: entra por el puerto {ingress_port}")
            if out_port is None:
                print(f"En {self.name}: no hay puerto de salida")
            else:
                print(f"En {self.name}: desconocido {dst_mac}, flooding → puerto {out_port}")
            return out_port, bits_in

# ---------------------- Router (L3) ----------------------
class Router:
    """
    Router con dos interfaces (left/right).
    - Reescribe SOLO MACs (L2) según la red de destino (/4).
    - Mantiene IP/puerto/payload.
    - ARP estático por lado: ip -> mac
    """
    def __init__(self, name, left_mac, left_ip, right_mac, right_ip):
        self.name = name
        self.left_mac  = int(left_mac)
        self.left_ip   = int(left_ip)
        self.right_mac = int(right_mac)
        self.right_ip  = int(right_ip)
        self.arp_left  = {}
        self.arp_right = {}

    def set_arp(self, side, ip_int, mac_int):
        if side == "left":
            self.arp_left[int(ip_int)] = int(mac_int)
        else:
            self.arp_right[int(ip_int)] = int(mac_int)

    @staticmethod
    def _same_net(a, b, mask=0xF0):   # /4
        return (a & mask) == (b & mask)

    def route(self, bits_in, ingress_side):
        print("\nLlega a Router")
        print_capas_desde_bits(bits_in, titulo="En el Router (entrada):")
        src_mac, dst_mac, src_ip, dst_ip, port, app, payload_bits = parse_bitstream(bits_in)

        # Verifica que venga dirigido a la MAC de la interfaz de entrada
        expect = self.left_mac if ingress_side == "left" else self.right_mac
        if dst_mac != expect:
            print(f"En {self.name}: la trama no es para esta interfaz (dst_mac={dst_mac:02X} ≠ {expect:02X})")
            return None, bits_in

        # Decide salida por prefijo
        if self._same_net(dst_ip, self.left_ip):
            egress = "left";  src_mac_out = self.left_mac;  dst_mac_out = self.arp_left.get(dst_ip)
        elif self._same_net(dst_ip, self.right_ip):
            egress = "right"; src_mac_out = self.right_mac; dst_mac_out = self.arp_right.get(dst_ip)
        else:
            print(f"En {self.name}: sin ruta hacia IP {dst_ip}")
            return None, bits_in

        if dst_mac_out is None:
            print(f"En {self.name}: falta ARP en {egress} para IP {dst_ip}")
            return None, bits_in

        out_bits = build_bitstream(src_mac_out, dst_mac_out, src_ip, dst_ip, port, app, payload_bits)
        print("\nSale de Router")
        print_capas_desde_bits(out_bits, titulo="En el Router (salida):")
        return egress, out_bits
