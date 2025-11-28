import network
import time
from machine import Pin, SoftI2C, ADC
import dht
import ujson
from umqtt.simple import MQTTClient
import ssd1306 

# --- CONFIGURAÇÃO DE HARDWARE ---
sensor = dht.DHT22(Pin(15))      
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)

# Atuadores
bomba_rele = Pin(26, Pin.OUT)    
exaustor_rele = Pin(27, Pin.OUT) 
luz_painel = Pin(13, Pin.OUT)    

# Configuração do OLED
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def mostrar_cockpit(temp, hum, luz, st_bomba, st_fan, st_luz):
    oled.fill(0)
    oled.text("CABINE F1", 30, 0)
    oled.text("T:{:.0f}C H:{:.0f}%".format(temp, hum), 0, 12)
    oled.hline(0, 25, 128, 1)
    
    oled.text("Bomba:", 0, 30)
    oled.text("ON" if st_bomba else "OFF", 60, 30)
    
    oled.text("Fan:", 0, 40)
    oled.text("ON" if st_fan else "OFF", 60, 40)

    oled.text("Luz:", 0, 50)
    oled.text("ON" if st_luz else "OFF", 60, 50)
    oled.show()

# --- CONEXÃO ---
print("Iniciando Sistema de Cockpit...")
# Limpa tela inicial
mostrar_cockpit(0,0,0,0,0,0)

print("Conectando Wi-Fi...", end="")
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect('Wokwi-GUEST', '')
while not wifi.isconnected(): 
    time.sleep(0.1)
    print(".", end="")
print(" OK!")

try:
    print("Conectando MQTT...", end="")
    client = MQTTClient("esp32-cockpit-full", "test.mosquitto.org")
    client.connect()
    print(" OK!")
except Exception as e:
    print(" Erro MQTT: ", e)

# --- LOOP PRINCIPAL ---
while True:
    try:
        sensor.measure() 
        temp = sensor.temperature()
        hum = sensor.humidity()
        luz = ldr.read()
        
        # 1. Controle de Temperatura (Bomba)
        st_bomba = False
        if temp > 32:
            bomba_rele.value(1)
            st_bomba = True
        else:
            bomba_rele.value(0)
            
        # 2. Controle de Humidade (Exaustor)
        st_fan = False
        if hum > 70:
            exaustor_rele.value(1)
            st_fan = True
        else:
            exaustor_rele.value(0)

        # 3. Controle de Luz (Painel)
        st_luz = False
        if luz > 1000: 
            luz_painel.value(1)
            st_luz = True
        else:
            luz_painel.value(0)

        # Atualiza Display
        mostrar_cockpit(temp, hum, luz, st_bomba, st_fan, st_luz)
        
        # Agora enviamos "luminosidade" (valor bruto) E "luz_painel" (status on/off)
        payload = ujson.dumps({
            "temp": temp, 
            "hum": hum, 
            "luminosidade": luz,       # <--- NOVO: Valor de 0 a 4095
            "bomba": st_bomba, 
            "fan": st_fan,
            "luz_painel": st_luz       # Renomeei para ficar claro que é o status do LED
        })
        client.publish("gian/projeto/cockpit", payload)
        print("Enviado: ", payload) 
        
    except OSError:
        print("Erro leitura sensor")
    except Exception as e:
        print("Erro geral: ", e)
    
    time.sleep(2)