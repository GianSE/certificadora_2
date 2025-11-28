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
bomba_rele = Pin(26, Pin.OUT)    # Relé 1: Bomba de Água
exaustor_rele = Pin(27, Pin.OUT) # Relé 2: Exaustor (NOVO)
luz_painel = Pin(13, Pin.OUT)    # LED: Luz do Painel

# Configuração do OLED
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def mostrar_cockpit(temp, hum, luz, st_bomba, st_fan, st_luz):
    oled.fill(0)
    oled.text(f"CABINE F1", 30, 0)
    
    # Dados Numéricos
    oled.text(f"T:{temp:.0f}C H:{hum:.0f}%", 0, 12)
    
    oled.hline(0, 25, 128, 1)
    
    # Status dos Equipamentos
    # Coluna 1
    oled.text("Bomba:", 0, 30)
    oled.text("ON" if st_bomba else "OFF", 60, 30)
    
    oled.text("Fan:", 0, 40)
    oled.text("ON" if st_fan else "OFF", 60, 40) # Mostra status do Exaustor

    oled.text("Luz:", 0, 50)
    oled.text("ON" if st_luz else "OFF", 60, 50)
        
    oled.show()

# --- CONEXÃO (Mantenha igual) ---
print("Iniciando Sistema de Cockpit...")
mostrar_cockpit(0,0,0,0,0,0)
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect('Wokwi-GUEST', '')
while not wifi.isconnected(): time.sleep(0.1)

try:
    client = MQTTClient("esp32-cockpit-full", "test.mosquitto.org")
    client.connect()
except:
    pass

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
            
        # 2. Controle de Humidade (Exaustor) - NOVO
        # Se a humidade passar de 70%, liga o ventilador para desembaçar
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

        # Atualiza Display e Envia MQTT
        mostrar_cockpit(temp, hum, luz, st_bomba, st_fan, st_luz)
        
        payload = ujson.dumps({
            "temp": temp, 
            "hum": hum, 
            "bomba": st_bomba, 
            "fan": st_fan,
            "luz": st_luz
        })
        client.publish("gian/projeto/cockpit", payload)
        
    except OSError:
        print("Erro sensor")
    
    time.sleep(1)