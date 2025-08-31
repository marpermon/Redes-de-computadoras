from clases import PC

if __name__ == "__main__":
    pc1 = PC("PC1", mac_int=7, ip_last_octet=110)
    pc2 = PC("PC2", mac_int=3, ip_last_octet=100)
    # App = "Facebook", mensaje = "Hola"
    pc1.enviar(pc2, "Facebook", "Hola", imprimir=True)
