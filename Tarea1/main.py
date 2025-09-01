from clases import *

def main():
    # Direccionamiento (8 bits)
    # Red 1: 0x10/4  Red 2: 0x20/4
    PC1 = PC("PC1", mac=3,   ip=0x11)   # 3, 17
    PC2 = PC("PC2", mac=11,  ip=0x21)   # 11, 33

    R1  = Router("Router1", left_mac=100, left_ip=0x12, right_mac=110, right_ip=0x22)  # 100/110, 18/34
    # ARP estático del router
    R1.set_arp("left",  PC1.ip, PC1.mac)
    R1.set_arp("right", PC2.ip, PC2.mac)

    SW1 = Switch("Switch de la RED 1")
    SW2 = Switch("Switch de la RED 2")
    puertos_sw1 = [1,2]  # 1: PC1, 2: Router-left
    puertos_sw2 = [5,6]  # 5: Router-right, 6: PC2

    # Menú
    print("Menú de Comunicación")
    print("1. PC de Isai a PC de Junior")
    print("2. PC de Junior a PC de Isai")
    opcion_dir = input("\nSelecciona una opción: ").strip()

    mensaje = input("\nIngrese el mensaje que desea enviar: ").strip()

    apps = ["Telegram", "WhatsApp", "Facebook"]
    print("\nIngrese por medio de cuál App se va a enviar el mensaje:")
    for i, a in enumerate(apps, 1): print(f"{i}. {a}")
    opc_app = input("\nSelecciona una opción: ").strip()
    try:
        app_name = apps[int(opc_app)-1]
    except:
        app_name = "Telegram"

    if opcion_dir == "1":
        print(f"\nHas seleccionado {app_name}.")
        # Envío desde PC1
        print("\n--- Encapsulación en PC Isai ---")
        bits = PC1.enviar(dst_pc=PC2, app_name=app_name, mensaje=mensaje)

        # IMPORTANTE: simular ARP/gateway sin tocar la PC:
        # Para el primer salto, la trama debe ir dirigida a la MAC del router (left).
        bits = rewrite_mac(bits, new_dst=R1.left_mac)

        # Switch 1
        print("\nEn Switch de la RED 1")
        SW1.forward(bits, ingress_port=1, puertos_disponibles=puertos_sw1)

        # Router (entra por la izquierda)
        _, bits = R1.route(bits, ingress_side="left")

        # Switch 2
        print("\nEn Switch de la RED 2")
        SW2.forward(bits, ingress_port=5, puertos_disponibles=puertos_sw2)

        # Llega a PC2
        print("\nLlega a PC de Junior")
        print_capas_desde_bits(bits, titulo="(Vista previa antes de PC de Junior):")
        print("\n--- Desencapsulación en PC de Junior ---")
        recibido = PC2.recibir(bits)
        print(f"\nMensaje final en aplicación: {recibido}")

    else:
        print(f"\nHas seleccionado {app_name}.")
        # Envío desde PC2
        print("\n--- Encapsulación en PC de Junior ---")
        bits = PC2.enviar(dst_pc=PC1, app_name=app_name, mensaje=mensaje)

        # Primer salto: dirigir a MAC del router (right)
        bits = rewrite_mac(bits, new_dst=R1.right_mac)

        # Switch 2
        print("\nEn Switch de la RED 2")
        SW2.forward(bits, ingress_port=6, puertos_disponibles=puertos_sw2)

        # Router (entra por la derecha)
        _, bits = R1.route(bits, ingress_side="right")

        # Switch 1
        print("\nEn Switch de la RED 1")
        SW1.forward(bits, ingress_port=2, puertos_disponibles=puertos_sw1)

        # Llega a PC1
        print("\nLlega a PC de Isai")
        print_capas_desde_bits(bits, titulo="(Vista previa antes de PC de Isai):")
        print("\n--- Desencapsulación en PC de Junior ---")
        recibido = PC1.recibir(bits)
        print(f"\nMensaje final en aplicación: {recibido}")

if __name__ == "__main__":
    main()


