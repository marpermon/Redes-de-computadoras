from clases import PC

if __name__ == "__main__":
    pc1 = PC("PC1", mac=7, ip=110)
    pc2 = PC("PC2", mac=3, ip=100)
    # App = "Facebook", mensaje = "Hola"
    pc1.enviar(pc2, "Facebook", "Hola")
