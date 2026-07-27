from machine import ADC, Pin, PWM, SoftI2C
from time import sleep
from servo import Servo

import dht
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

import ble_library
import bluetooth

import ssd1306
import framebuf

# 조도 센서 초기화 (LDR Pin 36)
cds = ADC(Pin(36))
cds.atten(ADC.ATTN_11DB)

cds_flag = 0

# 서보 모터 초기화 (Servo Pin 13)
motor = Servo(pin=13)

# 피에조 부저 초기화 (PWM Pin 23, 기본 주파수 1000Hz 설정)
piezo = PWM(Pin(23), freq=1000)
piezo.duty_u16(0)

# 부저 멜로디 정의
blindMelody = (524, 659, 784)
melody1 = (784, 784, 880, 880, 784, 784, 659)
melody2 = (523, 523, 784, 784, 880, 880, 784)

# RGB LED 핀 정의 (빨강 Pin 25, 초록 Pin 26, 파랑 Pin 27)
R = Pin(25, Pin.OUT)
G = Pin(26, Pin.OUT)
B = Pin(27, Pin.OUT)

# 정전식 터치 센서 4핀 정의
# [기본값] 회로 연결 명세서(스마트홈_회로연결.txt) 기준: D33, D32, D35, D34
touch1 = Pin(33, Pin.IN)
touch2 = Pin(32, Pin.IN)
touch3 = Pin(35, Pin.IN)
touch4 = Pin(34, Pin.IN)

# [선택] PRD_s.md 기준: D17, D5, D18, D19 (필요 시 아래 주석 해제 및 위 코드 주석 처리)
# touch1 = Pin(17, Pin.IN)
# touch2 = Pin(5, Pin.IN)
# touch3 = Pin(18, Pin.IN)
# touch4 = Pin(19, Pin.IN)

# DHT11 온습도 센서 초기화 (Pin 14)
d = dht.DHT11(Pin(14))

# TV (I2C LCD 16x2) 초기화 (SDA Pin 21, SCL Pin 22)
i2c = SoftI2C(sda=Pin(21), scl=Pin(22))
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.clear()

# LCD용 커스텀 특수문자 아이콘 정의 (온도계, 물방울)
temp_icon = bytearray([0x04, 0x0A, 0x0A, 0x0E, 0x0E, 0x1F, 0x1F, 0x0E])
humi_icon = bytearray([0x04, 0x04, 0x0A, 0x0A, 0x11, 0x1F, 0x1F, 0x0E])
lcd.custom_char(0, temp_icon)
lcd.custom_char(1, humi_icon)

# BLE 인스턴스 초기화 및 'ESP_dd' 장치명으로 페어링 시작 (웹 검색 필터인 'ESP_' 매칭)
ble = bluetooth.BLE()
p = ble_library.BLESimplePeripheral(ble, "ESP_dd")

# OLED 디스플레이 초기화 (기존의 SoftI2C 'i2c' 버스 인스턴스 공유하여 충돌 방지)
display2 = ssd1306.SSD1306_I2C(128, 64, i2c)

display2.fill(0)
display2.show()

# 블루투스 수신 이벤트 핸들러
def on_rx(v): 
    print(v)
    # '1' 수신 시: TV(LCD)에 현재 온습도 표시 및 웹 브라우저로 블루투스 송신
    if v == '1':
        lcd.clear()
        print("1")
        try:
            # 온습도 측정
            d.measure()
            temp = str(int(d.temperature()))
            humi = str(int(d.humidity()))
            lcd.clear()
            
            lcd.move_to(0, 0)
            lcd.putchar(chr(0)) # 온도계 아이콘
            lcd.putstr("temp : ")
            lcd.putstr(temp)
            lcd.putstr("C")
            
            lcd.move_to(0, 1)
            lcd.putchar(chr(1)) # 물방울 아이콘
            lcd.putstr("humi : ")
            lcd.putstr(humi)
            lcd.putstr("%")
            
            # 웹 브라우저 대시보드 화면 동기화를 위해 블루투스 송신 (p.send)
            p.send("temp : " + temp + "\n")
            p.send("humi : " + humi + "\n")
        except Exception as e:
            print("DHT11 sensor error:", e)
            lcd.move_to(0, 0)
            lcd.putstr("DHT11 Read Error")
            p.send("temp : Err\n")
            p.send("humi : Err\n")
        
    # '2' 수신 시: TV(LCD)에 조도 센서 측정값 표시 및 웹 브라우저로 블루투스 송신
    if v == '2':
        lcd.clear()
        try:
            cds_value = cds.read()
            lcd.move_to(0, 0)
            lcd.putstr(str(cds_value))
            
            if cds_value > 4000:   
                lcd.move_to(0, 1)
                lcd.putstr("It's dark")
            else:
                lcd.move_to(0, 1)
                lcd.putstr("It's bright")
                
            # 웹 브라우저 대시보드 화면 동기화를 위해 조도 값 블루투스 송신 (p.send)
            p.send(str(cds_value) + "\n")
        except Exception as e:
            print("CdS sensor error:", e)
            lcd.move_to(0, 0)
            lcd.putstr("CdS Read Error")
            p.send("0\n")

    # '3' 수신 시: LCD 백라이트 켜기
    if v == '3':
        lcd.backlight_on()
        
    # '4' 수신 시: LCD 백라이트 끄기
    if v == '4':
        lcd.backlight_off()
    
    # '5' 수신 시: 멜로디 1 (학교종) 부저 재생 (50% 듀티 사이클로 출력)
    if v == '5':
        piezo.duty_u16(32768)
        for i in melody1:
            piezo.freq(i)
            sleep(0.5)
        piezo.duty_u16(0) 

    # '6' 수신 시: 멜로디 2 (작은별) 부저 재생 (50% 듀티 사이클로 출력)
    if v == '6':
        piezo.duty_u16(32768)
        for i in melody2:
            piezo.freq(i)
            sleep(0.5)
        piezo.duty_u16(0) 
    
    # '7' 수신 시: RGB LED 전체 켜기
    if v == '7':
        R.on()
        G.on()
        B.on()        
    
    # '8' 수신 시: RGB LED 전체 끄기
    if v == '8':
        R.off()
        G.off()
        B.off()    
    
    # '9' 수신 시: OLED에 Snoopy PBM 단색 비트맵 이미지 드로잉 (예외 안전 처리)
    if v == '9':
        image_paths = ['img/snoppy.pbm', 'lib/kitty.pbm', 'snoppy.pbm', 'kitty.pbm']
        image_loaded = False
        for path in image_paths:
            try:
                with open(path, 'rb') as f:
                    f.readline() # PBM 포맷 헤더 스킵
                    f.readline() # 이미지 크기 헤더 스킵
                    data = bytearray(f.read())
                fb = framebuf.FrameBuffer(data, 128, 64, framebuf.MONO_HLSB)
                display2.invert(0)
                display2.fill(0)
                display2.blit(fb, 0, 0)
                display2.show()
                p.send("OLED : Image Loaded\n")
                image_loaded = True
                break
            except Exception:
                continue
        
        if not image_loaded:
            print("OLED Image file not found")
            display2.fill(0)
            display2.text("Snoopy image", 15, 20)
            display2.text("not found!", 20, 35)
            display2.show()
            p.send("OLED : File Not Found\n")

# 블루투스 수신 데이터 바인딩
p.on_write(on_rx)

# 터치 센서 이전 상태 저장용 변수
last_t1 = 0
last_t2 = 0
last_t3 = 0
last_t4 = 0

# 메인 무한 루프
while True:
    # 조도 밝기 변화에 따른 모터 및 멜로디 동작
    cds_value = cds.read()
    
    if cds_value > 4000 and cds_flag == 1:
        piezo.duty_u16(32768) # 50% 듀티 사이클로 변경
        for i in blindMelody:
            piezo.freq(i)
            sleep(0.3)
        piezo.duty_u16(0) 
        motor.move(180)
        cds_flag = 0       
        
    elif cds_value <= 4000 and cds_flag == 0:
        motor.move(90)
        cds_flag = 1 
        
    # 터치 센서 실시간 값 읽기
    t1 = touch1.value()
    t2 = touch2.value()
    t3 = touch3.value()
    t4 = touch4.value()
    
    # 터치 센서 접촉 감지 시점에만 단발적으로 LED 상태 변경 (엣지 트리거)
    # 이를 통해 웹에서 보낸 BLE LED 제어 명령이 루프에 의해 계속 덮어쓰여지는 것을 방지합니다.
    if t1 and not last_t1:
        print("Button 1 touched")
        R.on()
        G.off()
        B.off()
        
    elif t2 and not last_t2:
        print("Button 2 touched")
        R.on()
        G.on()
        B.off()
    
    elif t3 and not last_t3:
        print("Button 3 touched")
        R.on()
        G.off()
        B.on()
        
    elif t4 and not last_t4:
        print("Button 4 touched")
        R.off()
        G.off()
        B.off()

    # 이전 상태 기록 업데이트
    last_t1 = t1
    last_t2 = t2
    last_t3 = t3
    last_t4 = t4

    sleep(0.5)
