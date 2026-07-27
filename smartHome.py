from machine import ADC, Pin, PWM, SoftI2C
import time
import network
import ntptime
from neopixel import NeoPixel
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

import ble_library
import bluetooth
import ssd1306
import framebuf

# ==========================================
# 1. Wi-Fi 및 시간 설정 (한국 시간)
# ==========================================
WIFI_SSID = "ICEE"
WIFI_PASSWORD = "icee2026"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("WiFi 연결 중...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
            print(".", end="")
    print("\nWiFi 연결 완료!")
    try:
        ntptime.settime() # UTC 시간 동기화
        print("시간 동기화 완료")
    except Exception as e:
        print("시간 동기화 실패:", e)
        
# ==========================================
# 2. 하드웨어 핀 맵핑 초기화
# ==========================================
# 터치 센서
touch1 = Pin(17, Pin.IN) # 무드등 스위치
touch4 = Pin(19, Pin.IN) # 3초 길게 누르기 알람 해제

# 네오픽셀 (12구)
pin = Pin(14, Pin.OUT)
np = NeoPixel(pin, 12) 

# 피에조 부저
piezo = PWM(Pin(23), freq=1000)
piezo.duty_u16(0)

# I2C 통신 (LCD & OLED 공용)
i2c = SoftI2C(sda=Pin(21), scl=Pin(22))
try:
    lcd = I2cLcd(i2c, 0x27, 2, 16) # LCD
    oled = ssd1306.SSD1306_I2C(128, 64, i2c) # OLED (ssd1306 prefix 추가)
    print("디스플레이 초기화 완료")
except Exception as e:
    print("디스플레이 초기화 에러:", e)

# ==========================================
# 3. 변수 (상태 관리)
# ==========================================
target_alarm_mins = -1
wake_mins = -1
is_alarming = False
is_sunrise_active = False
mood_light_on = False

# 터치 제어용 변수
touch1_last_state = 0
touch4_press_start = 0
touch4_pressing = False

# 블루투스 초기화
ble = bluetooth.BLE()
p = ble_library.BLESimplePeripheral(ble, "ESP_dd") # ble_library prefix 추가

# ==========================================
# 4. 기능 함수들
# ==========================================
def get_kst_time():
    # KST = UTC + 9시간 (32400초)
    t = time.localtime(time.time() + 32400)
    return t

def set_neopixel(r, g, b):
    for i in range(12):
        np[i] = (r, g, b)
    np.write()

def calculate_smart_wakeup():
    global target_alarm_mins, wake_mins
    if target_alarm_mins < 0: return
    
    t = get_kst_time()
    current_mins = t[3] * 60 + t[4]
    
    # 입면 시간(15분) 추가
    sleep_start_mins = current_mins + 15
    if target_alarm_mins < sleep_start_mins:
        target_alarm_mins += 1440 # 다음 날로 계산
        
    diff = target_alarm_mins - sleep_start_mins
    cycles = diff // 90 # 90분 수면 주기 횟수
    cycle_end_mins = sleep_start_mins + (cycles * 90)
    
    # 수면 주기가 타겟 시간 40분 이내에 끝난다면 앞당김
    if target_alarm_mins - 40 <= cycle_end_mins <= target_alarm_mins:
        wake_mins = cycle_end_mins % 1440
    else:
        wake_mins = target_alarm_mins % 1440
        
    wake_h = wake_mins // 60
    wake_m = wake_mins % 60
    
    # 웹으로 계산 결과 전송
    msg = "wake : {:02d}{:02d}\n".format(wake_h, wake_m)
    p.send(msg)
    
    # LCD 업데이트
    lcd.move_to(0, 1)
    lcd.putstr("Wake: {:02d}:{:02d}    ".format(wake_h, wake_m))
    
    # OLED 수면 모드 전환
    oled.fill(0)
    oled.text("Zzz...", 40, 30)
    oled.show()

def on_rx(data):
    global target_alarm_mins, is_alarming, mood_light_on
    msg = data.decode().strip()
    
    if msg == '1': # 수면 시작
        calculate_smart_wakeup()
    elif msg == '2': # 무드등 수동 토글
        mood_light_on = not mood_light_on
        if mood_light_on: set_neopixel(100, 100, 80)
        else: set_neopixel(0, 0, 0)
    elif msg == '3': # 강제 알람 테스트
        is_alarming = True
    elif msg.startswith('T'): # 시간 설정 (예: T0700)
        h = int(msg[1:3])
        m = int(msg[3:5])
        target_alarm_mins = h * 60 + m
        lcd.move_to(0, 1)
        lcd.putstr("Set: {:02d}:{:02d}    ".format(h, m))

p.on_write(on_rx)

# ==========================================
# 5. 메인 루프 (Main Loop)
# ==========================================
connect_wifi()
lcd.clear()

last_time_update = 0

while True:
    current_time_ms = time.ticks_ms()
    t = get_kst_time()
    current_mins = t[3] * 60 + t[4]
    
    # --------------------------------------
    # A. 화면 업데이트 (1초마다)
    # --------------------------------------
    if time.ticks_diff(current_time_ms, last_time_update) > 1000:
        lcd.move_to(0, 0)
        lcd.putstr("Time: {:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5]))
        last_time_update = current_time_ms

    # --------------------------------------
    # B. 일출 시뮬레이션 및 알람 로직
    # --------------------------------------
    if wake_mins >= 0 and not is_alarming:
        diff_mins = wake_mins - current_mins
        if diff_mins < 0: diff_mins += 1440
        
        if diff_mins == 30: # T-30: 보라/피치 파스텔톤
            set_neopixel(10, 0, 10)
        elif diff_mins == 15: # T-15: 코랄/옐로우
            set_neopixel(50, 20, 0)
        elif diff_mins == 0: # T-0: 정각 알람!
            set_neopixel(255, 200, 150) # 웜화이트 최대 밝기
            is_alarming = True
            wake_mins = -1 # 알람 초기화
            
            oled.fill(0)
            oled.text("WAKE UP!", 30, 20)
            oled.show()

    # 부저 비프음 (알람 작동 중일 때)
    if is_alarming:
        if (current_time_ms // 500) % 2 == 0:
            piezo.duty_u16(32768) # buzzer -> piezo로 통일 및 duty -> duty_u16(50% 볼륨)으로 수정
            piezo.freq(1000)
        else:
            piezo.duty_u16(0)

    # --------------------------------------
    # C. 터치 센서 로직
    # --------------------------------------
    # 터치 1 (무드등 토글 - 디바운스 적용)
    t1_val = touch1.value()
    if t1_val == 1 and touch1_last_state == 0:
        mood_light_on = not mood_light_on
        if mood_light_on: set_neopixel(100, 100, 80)
        else: set_neopixel(0, 0, 0)
    touch1_last_state = t1_val

    # 터치 4 (3초 길게 누르기 알람 해제)
    if is_alarming:
        if touch4.value() == 1:
            if not touch4_pressing:
                touch4_press_start = current_time_ms
                touch4_pressing = True
            
            # 누르고 있는 시간 계산
            elapsed = time.ticks_diff(current_time_ms, touch4_press_start)
            
            # OLED 로딩 바 애니메이션 업데이트
            oled.fill_rect(10, 45, 108, 10, 0) # 이전 바 지우기
            bar_width = int((elapsed / 3000) * 100)
            if bar_width > 100: bar_width = 100
            oled.rect(14, 45, 102, 8, 1) # 테두리
            oled.fill_rect(15, 46, bar_width, 6, 1) # 채우기
            oled.show()
            
            # 3초(3000ms) 도달 시 알람 종료!
            if elapsed >= 3000:
                is_alarming = False
                touch4_pressing = False
                piezo.duty_u16(0) # buzzer.duty(0) -> piezo.duty_u16(0)으로 수정
                
                oled.fill(0)
                oled.text("Good Morning!", 15, 30)
                oled.show()
                # 조명은 무드등 상태로 계속 유지됨 (PRD 요구사항)
        else:
            if touch4_pressing:
                # 손을 중간에 떼면 초기화
                touch4_pressing = False
                oled.fill_rect(10, 45, 108, 10, 0)
                oled.show()
    
    time.sleep_ms(10) # CPU 부하 감소를 위한 짧은 대기 추가
