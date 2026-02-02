import network
import socket
from machine import Pin, PWM
import time

# ---------- CONFIGURACIÓN WIFI ----------
SSID = "ESP32"           # SSID de tu Raspberry Pi AP
PASSWORD = "12345678"    # Contraseña del AP
UDP_PORT = 5005          # Puerto UDP para recibir los ángulos

# IP ESTÁTICA
STATIC_IP = "192.168.4.2"
NETMASK   = "255.255.255.0"
GATEWAY   = "192.168.4.1"
DNS       = "192.168.4.1"

# ---------- CONFIGURACIÓN SERVOS ----------
servo_pins = [15, 16, 17, 18, 4]
min_us = 500
max_us = 2500
freq = 50

servos = []
for pin in servo_pins:
    pwm = PWM(Pin(pin))
    pwm.freq(freq)
    servos.append(pwm)

def angle_to_duty(angle):
    us = min_us + (max_us - min_us) * angle / 180
    return int(us * 1023 / 20000)

def move_servos(values):
    for i in range(5):
        angle = max(0, min(180, values[i]))
        servos[i].duty(angle_to_duty(angle))

# ---------- FUNCIONES WIFI ----------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Configurar IP estática antes de conectar
    wlan.ifconfig((STATIC_IP, NETMASK, GATEWAY, DNS))

    while not wlan.isconnected():
        try:
            print("Intentando conectar a Wi-Fi con IP estática...")
            wlan.connect(SSID, PASSWORD)
            t_start = time.ticks_ms()
            while not wlan.isconnected():
                if time.ticks_diff(time.ticks_ms(), t_start) > 10000:  # timeout 10 s
                    print("Timeout, reintentando...")
                    wlan.disconnect()
                    break
                time.sleep(0.5)
        except Exception as e:
            print("Error conexión:", e)
            time.sleep(2)

    print("Conectado! IP:", wlan.ifconfig())
    return wlan

# ---------- LOOP PRINCIPAL ----------
while True:
    try:
        wlan = connect_wifi()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.1)
        sock.bind(("0.0.0.0", UDP_PORT))
        print("Esperando datos UDP...")

        while wlan.isconnected():
            try:
                data, addr = sock.recvfrom(64)
                line = data.decode().strip()
                print(f"Datos recibidos de {addr}: {line}")  # <-- mostramos los datos recibidos
                parts = line.split(",")
                if len(parts) == 5:
                    values = [int(p) for p in parts]
                    move_servos(values)
            except OSError:
                pass
            except Exception as e:
                print("Error:", e)

        print("Wi-Fi desconectada, reiniciando socket...")
        sock.close()

    except Exception as e:
        print("Error general:", e)
        time.sleep(2)
