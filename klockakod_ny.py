########################################
#                                      #
#          KLOCKA STYRNING             #
#        RASPBERRY PI ZERO 2W          #
#                                      #
#         HW: Melvin Olsson            #
#        SW: William Andersson         #
#                                      #
#           Version: 2.2               #
#            2024-11-02                #
########################################

######## BIBLIOTEK ########
import gpiozero  # Installera med: sudo apt install python3-gpiozero
from gpiozero import Button
import rpi_ws281x  # Installera med: pip3 install rpi_ws281x --break-system-packages
from rpi_ws281x import Color, PixelStrip, ws
import time
import datetime
import threading
import sys
import traceback

######## VARIABLER ########

# LED-stripkonfiguration:
LED_COUNT = 154        # Antal LED-pixlar.
LED_PIN = 18           # GPIO-pin ansluten till pixlarna.
LED_FREQ_HZ = 800000   # LED-signalens frekvens i hertz (vanligtvis 800kHz).
LED_DMA = 5            # DMA-kanal för att generera signalen.
LED_BRIGHTNESS = 255   # Maximal ljusstyrka (0-255).
LED_INVERT = False     # Invertera signalen (används med NPN-transistor).
LED_CHANNEL = 0
LED_STRIP = ws.SK6812_STRIP  # Typ av LED-strip, anpassad för WWA.

# Platshållare för ingen LED
X = 199

# LED-FÄRGER (Amber, Kallvit, Varmvit)
color_options = [
    Color(128, 255, 0),    # Standard
    Color(0, 255, 0),      # Mycket kallvit
    Color(0, 255, 64),     # Kallvit
    Color(0, 255, 128),    # Neutralvit
    Color(0, 192, 192),    # Mjukvit
    Color(0, 128, 255),    # Varmvit
    Color(0, 64, 255),     # Varm glödlampa
    Color(0, 0, 255),      # Mycket varm (stearinljus)
]

# Initiala inställningar
currentColorIndex = 0
currentColor = color_options[currentColorIndex]
currentBrightness = 200  # Standardljusstyrka (0-255)

# Knappinställningar
BUTTON_PIN = 26            # GPIO-pin där knappen är ansluten
BUTTON_HOLD_TIME = 1       # Tid i sekunder för att registrera ett knapphåll
BRIGHTNESS_STEP = 5        # Stegstorlek för ljusstyrkejustering
MIN_BRIGHTNESS = 10        # Minimal ljusstyrka
MAX_BRIGHTNESS = 255       # Maximal ljusstyrka
BOUNCE_TIME = 0.1         # Debounce-tid för knappen i sekunder

######## LED-MATRIS PINOUT ########

# LED-MATRISER (ENBART FÖR 1200mm KRETSKORT)
ledslots_leds = [ #list(range(10, 17)),
    [list(range(0, 6))], #1
    [list(range(7, 13))], #2
    [list(range(14, 21))], #3
    [list(range(22, 29))], #4
    [list(range(30, 37))], #5
    [list(range(0, 45))], #6
    [list(range(0, 53))], #7
    [list(range(0, 61))], #8
    [list(range(0, 69))], #9
    [list(range(0, 77))], #10
    [list(range(0, 85))], #11
    [list(range(0, 93))], #12
    [list(range(0, 101))], #13
    [list(range(0, 109))], #14
    [list(range(0, 117))], #15
    [list(range(0, 125))], #16
    [list(range(0, 133))], #17
    [list(range(0, 141))], #18
    [list(range(0, 149))], #19
    [list(range(0, 157))], #20
    [list(range(0, 165))], #21
    [list(range(0, 173))], #22
    [list(range(0, 181))], #23
    [list(range(0, 189))], #24
    [list(range(0, 197))], #25
    [list(range(0, 205))], #26
    [list(range(0, 213))], #27
    [list(range(0, 221))], #28
    [list(range(0, 229))], #29
    [list(range(0, 237))], #30
    [list(range(0, 245))], #31
    [list(range(0, 253))], #32
    [list(range(0, 261))], #33
    [list(range(0, 269))], #34
    [list(range(0, 277))], #35
    [list(range(0, 285))], #36
    [list(range(0, 293))], #37
    [list(range(0, 301))], #38
    [list(range(0, 309))], #39
    [list(range(0, 317))], #40
    [list(range(0, 325))], #41
    [list(range(0, 333))], #42
    [list(range(0, 341))], #43
    [list(range(0, 349))], #44
    [list(range(0, 357))], #45
    [list(range(0, 365))], #46
    [list(range(0, 373))], #47
    [list(range(0, 381))], #48
    [list(range(0, 389))], #49
    [list(range(0, 397))], #50
    [list(range(0, 405))], #51
    [list(range(0, 413))], #52
    [list(range(0, 421))], #53
    [list(range(0, 429))], #54
    [list(range(0, 437))], #55
    [list(range(0, 445))], #56
    [list(range(0, 453))], #57
    [list(range(0, 461))], #58
    [list(range(0, 469))], #59
    [list(range(0, 477))], #60
    [list(range(0, 485))], #61
    [list(range(0, 493))], #62
    [list(range(0, 501))], #63
    [list(range(0, 509))], #64
    [list(range(0, 517))], #65
    [list(range(0, 525))], #66
    [list(range(0, 533))], #67
    [list(range(0, 541))], #68
    [list(range(0, 549))], #69
    [list(range(0, 557))], #70
    [list(range(0, 565))], #71
    [list(range(0, 573))], #72
    [list(range(0, 581))], #73
    [list(range(0, 589))], #74
    [list(range(0, 597))], #75
]
hour_leds = [
    [35,36,37,38,39,40,41, 14,15,16,17,18,19,20, 25,26,27,28,29,30,31],  # ETT
    [42,43,44,45,46,47,48, 13,14,15,16,17,18,19, 32,33,34,35,36,37,38],  # TVÅ
    [49,50,51,52,53,54,55, 12,13,14,15,16,17,18, 39,40,41,42,43,44,45],  # TRE
    [200,201,202,203,204,205,206, 58,59,60,61,62,63,64, 65,66,67,68,69,70,71, 71,72,73,74,75,76,77],  # FYRA
    [57,58,59,60,61,62,63, 72,73,74,75,76,77,78, 79,80,81,82,83,84,85],  # FEM
    [56,57,58,59,60,61,62, 11,12,13,14,15,16,17, 46,47,48,49,50,51,52],  # SEX
    [73,74,75,76,77,78,79, 86,87,88,89,90,91,92, 93,94,95,96,97,98,99],  # SJU
    [31,32,33,34,35,36,37, 53,54,55,56,57,58,59, 60,61,62,63,64,65,66, 67,68,69,70,71,72,73],  # ÅTTA
    [21,22,23,24,25,26,27, 28,29,30,31,32,33,34, 47,48,49,50,51,52,53],  # NIO
    [100,101,102,103,104,105,106, 107,108,109,110,111,112,113, 114,115,116,117,118,119,120],  # TIO
    [29,30,31,32,33,34,35, 74,75,76,77,78,79,80, 81,82,83,84,85,86,87, 88,89,90,91,92,93,94],  # ELVA
    [95,96,97,98,99,100,101, 115,116,117,118,119,120,121, 122,123,124,125,126,127,128, 129,130,131,132,133,134,135]  # TOLV
]

word_leds = [
    [0,1,2,3,4,5,6, 133,134,135,136,137,138,139, 140,141,142,143,144,145,146],  # KLOCKAN ÄR
    [7,8,9,10,11,12,13, 130,131,132,133,134,135,136],  # FEM I
    [315,316,317,318,319,320,321, 347,348,349,350,351,352,353],  # TIO I
    [14,15,16,17,18,19,20, 127,128,129,130,131,132,133, 137,138,139,140,141,142,143, 144,145,146,147,148,149,150],  # KVART I
    [21,22,23,24,25,26,27, 124,125,126,127,128,129,130, 134,135,136,137,138,139,140, 151,152,153,154,155,156,157],  # TJUGO I
    [7,8,9,10,11,12,13, 130,131,132,133,134,135,136, 137,138,139,140,141,142,143, 350,351,352,353,354,355,356, 357,358,359,360,361,362,363, 364,365,366,367,368,369,370, 371,372,373,374,375,376,377],  # FEM I HALV
    [350,351,352,353,354,355,356, 357,358,359,360,361,362,363, 364,365,366,367,368,369,370, 371,372,373,374,375,376,377],  # HALV
    [7,8,9,10,11,12,13, 130,131,132,133,134,135,136, 137,138,139,140,141,142,143, 28,29,30,31,32,33,34, 118,119,120,121,122,123,124, 151,152,153,154,155,156,157, 350,351,352,353,354,355,356, 357,358,359,360,361,362,363, 364,365,366,367,368,369,370, 371,372,373,374,375,376,377],  # FEM ÖVER HALV
    [7,8,9,10,11,12,13, 130,131,132,133,134,135,136, 137,138,139,140,141,142,143, 28,29,30,31,32,33,34, 118,119,120,121,122,123,124],  # FEM ÖVER
    [315,316,317,318,319,320,321, 347,348,349,350,351,352,353, 28,29,30,31,32,33,34, 118,119,120,121,122,123,124],  # TIO ÖVER
    [14,15,16,17,18,19,20, 127,128,129,130,131,132,133, 137,138,139,140,141,142,143, 144,145,146,147,148,149,150, 28,29,30,31,32,33,34, 118,119,120,121,122,123,124],  # KVART ÖVER
    [21,22,23,24,25,26,27, 124,125,126,127,128,129,130, 134,135,136,137,138,139,140, 151,152,153,154,155,156,157, 28,29,30,31,32,33,34, 118,119,120,121,122,123,124]  # TJUGO ÖVER
]

# Små lampor som visar minut
minut_led_nr1 = 153
minut_led_nr2 = 152
minut_led_nr3 = 151
minut_led_nr4 = 150

minute_leds = [
    [minut_led_nr1],  # Minut 1
    [minut_led_nr1, minut_led_nr2],  # Minut 2
    [minut_led_nr1, minut_led_nr2, minut_led_nr3],  # Minut 3
    [minut_led_nr1, minut_led_nr2, minut_led_nr3, minut_led_nr4]  # Minut 4
]

######## INITIALISERING ########

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT,
                   LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)

clockStarted = False
currentTime = datetime.datetime.now()
press_time = 0  # Variabel för att lagra tidpunkten när knappen trycks ned
brightnessIncreasing = True # Startar med att öka ljusstyrkan när knappen hålls inne

######## FUNKTIONER ########

### LED-FUNKTIONER ###
def SetColor(fStrip, fColor):
    for i in range(fStrip.numPixels()):
        fStrip.setPixelColor(i, fColor)
    fStrip.show()


def ClearLeds(fStrip):
    for i in range(fStrip.numPixels()):
        fStrip.setPixelColor(i, Color(0, 0, 0))
    fStrip.show()


def UpdateTime(fStrip, fTime, fColor, fBrightness):
    ClearLeds(fStrip)                   # Rensa LEDs innan ändring
    fStrip.setBrightness(fBrightness)   # Ställ in önskad ljusstyrka

    # Tänd "KLOCKAN ÄR"
    for iLed in word_leds[0]:
        if iLed != X:
            fStrip.setPixelColor(iLed, fColor)

    # Hämta aktuell timme och minut
    minute = fTime.minute
    hour = fTime.hour % 12  # Konvertera till 12-timmarsformat
    if hour == 0:
        hour = 12  # Hantera midnatt som 12

    # Justera timme baserat på minut
    display_hour = hour
    if minute >= 25:
        display_hour += 1
        if display_hour > 12:
            display_hour = 1  # Återställ till 1 efter 12

    # Mappa timme till index i hour_leds
    hour_index = (display_hour - 1)  # Nollbaserat index

    # Bestäm vilka ord som ska tändas baserat på aktuell minut
    if minute >= 0 and minute < 5:
        # "KLOCKAN ÄR" + timme
        words_to_light = []
    elif minute >= 5 and minute < 10:
        # "Fem Över" + timme
        words_to_light = word_leds[8]
    elif minute >= 10 and minute < 15:
        # "Tio Över" + timme
        words_to_light = word_leds[9]
    elif minute >= 15 and minute < 20:
        # "Kvart Över" + timme
        words_to_light = word_leds[10]
    elif minute >= 20 and minute < 25:
        # "Tjugo Över" + timme
        words_to_light = word_leds[11]
    elif minute >= 25 and minute < 30:
        # "Fem I Halv" + nästa timme
        words_to_light = word_leds[5]
    elif minute >= 30 and minute < 35:
        # "Halv" + nästa timme
        words_to_light = word_leds[6]
    elif minute >= 35 and minute < 40:
        # "Fem Över Halv" + nästa timme
        words_to_light = word_leds[7]
    elif minute >= 40 and minute < 45:
        # "Tjugo I" + nästa timme
        words_to_light = word_leds[4]
    elif minute >= 45 and minute < 50:
        # "Kvart I" + nästa timme
        words_to_light = word_leds[3]
    elif minute >= 50 and minute < 55:
        # "Tio I" + nästa timme
        words_to_light = word_leds[2]
    elif minute >= 55 and minute < 60:
        # "Fem I" + nästa timme
        words_to_light = word_leds[1]
    else:
        words_to_light = []

    # Tänd valda ord
    for iLed in words_to_light:
        if iLed != X:
            fStrip.setPixelColor(iLed, fColor)

    # Tänd timmen
    for iLed in hour_leds[hour_index % 12]:
        if iLed != X:
            fStrip.setPixelColor(iLed, fColor)

    # Tänd minut-LEDs för extra minuter (1-4)
    extra_minutes = minute % 5
    if extra_minutes > 0:
        for i in range(extra_minutes):
            led_index = minute_leds[extra_minutes - 1][i]
            if led_index != X:
                fStrip.setPixelColor(led_index, fColor)

    # Uppdatera LEDs
    fStrip.show()

### KNAPPHANTERING ###
button = Button(BUTTON_PIN, pull_up=True, hold_time=BUTTON_HOLD_TIME, bounce_time=BOUNCE_TIME)

def adjust_brightness():
    global currentBrightness, brightnessIncreasing
    brightnessIncreasing = not brightnessIncreasing
    
    while button.is_pressed:
        if brightnessIncreasing:
            currentBrightness += BRIGHTNESS_STEP
            if currentBrightness >= MAX_BRIGHTNESS:
                currentBrightness = MAX_BRIGHTNESS
        else:
            currentBrightness -= BRIGHTNESS_STEP
            if currentBrightness <= MIN_BRIGHTNESS:
                currentBrightness = MIN_BRIGHTNESS

        # Uppdatera ljusstyrkan på strippen
        strip.setBrightness(currentBrightness)
        strip.show()

        time.sleep(0.05)  # Justera för mjuk övergång

    # När justeringen är klar, uppdatera klockan med aktuell ljusstyrka
    currentTime = datetime.datetime.now()
    UpdateTime(strip, currentTime, currentColor, currentBrightness)

def on_button_pressed():
    global press_time
    press_time = time.time()
    print("Knapp nedtryckt vid {:.2f}".format(press_time))

def on_button_released():
    global currentColorIndex, currentColor
    release_time = time.time()
    hold_duration = release_time - press_time
    print("Knapp släppt vid {:.2f}, hålltid: {:.2f} sekunder".format(release_time, hold_duration))
    if hold_duration < BUTTON_HOLD_TIME:
        # Knappen klickades, ändra färg
        currentColorIndex = (currentColorIndex + 1) % len(color_options)
        currentColor = color_options[currentColorIndex]
        # Uppdatera displayen med den nya färgen
        currentTime = datetime.datetime.now()
        UpdateTime(strip, currentTime, currentColor, currentBrightness)
        print("Färg ändrad till alternativ {}".format(currentColorIndex + 1))
    else:
        # Knappen hölls ned längre än hold_time
        print("Knappen hölls ned längre än hold_time")

def on_button_held():
    print("Knappen hålls ned, startar ljusstyrkejustering")
    threading.Thread(target=adjust_brightness).start()

button.when_pressed = on_button_pressed
button.when_released = on_button_released
button.when_held = on_button_held

######## HUVUDLOOP ########
while True:  # Yttre loop för att hantera omstarter och fel
    try:
        ######## KLOCKSTART ########
        if not clockStarted:  # Starta klockan
            strip.begin()  # Initiera LEDs
            ClearLeds(strip)

            ######## KLOCKA UPPDATERA TID FÖRSTA START ########
            currentTime = datetime.datetime.now()
            UpdateTime(strip, currentTime, currentColor, currentBrightness)
            old_minute = currentTime.minute

            clockStarted = True
            print("Klockan är igång")

        while clockStarted:  # Klockans loop
            # Hämta aktuell tid
            currentTime = datetime.datetime.now()

            # Om en ny minut har passerat, uppdatera klockan
            if currentTime.minute != old_minute:
                UpdateTime(strip, currentTime, currentColor, currentBrightness)
                print("Uppdaterad tid: {}:{}:{}".format(
                    currentTime.hour, currentTime.minute, currentTime.second))
                old_minute = currentTime.minute

            time.sleep(1)  # Vänta en sekund innan nästa kontroll

    except Exception as e:
        print("Ett fel inträffade: ", e)
        traceback.print_exc()  # Skriv ut detaljerad felinformation
        print("Startar om loopen...")
        clockStarted = False
        time.sleep(2)  # Vänta lite innan omstart

    time.sleep(1)  # Vänta 1 sekund innan nästa iteration av den yttre loopen
