import os
import sys
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from time import sleep, time, localtime, strftime
import ST7735
from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError
from enviroplus import gas

try:
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
import subprocess


#date data for gdoc
os.chdir('//home//pi')
now = datetime.now()
today = now.strftime('%m/%d/%y %H:%M')

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

#create BME280 instance
bme280 = BME280()
bme280.get_pressure()
#Read BME280 sensor (humidity, carbon monoxide)
humidity = bme280.get_humidity()
pressure = bme280.get_pressure()
#create PMS instance
pms5003 = PMS5003()
try:
    readings=pms5003.read()
    #raise ReadTimeoutError
except ReadTimeoutError:
    pms5003=PMS5003()
    readings=pms5003.read()
    #LCD instance
    MESSAGE = 'Starting Program'
    st7735 = ST7735.ST7735(port=0, cs=1, dc=9, backlight=12, rotation=270, spi_speed_hz=10000000)
    st7735.begin()
    WIDTH = st7735.width
    HEIGHT = st7735.height
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0 , 0))
    draw = ImageDraw.Draw(img)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
    size_x, size_y = draw.textsize(MESSAGE, font)
    text_x=160
    text_y=(80 - size_y) // 2
    t_start = time.time()
    for i in range(210):
        proximity = ltr559.get_proximity()
        if proximity > 1500:
            f.close()
            raise KeyboardInterrupt
        x=(time.time() - t_start) * 100
        x %= (size_x + 200)
        draw.rectangle((0, 0, 160, 80), (0, 0, 0))
        draw.text((int(text_x - x), text_y), MESSAGE, font=font, fill=(255, 255, 255))
        st7735.display(img)
        i
    #attain individual pm sensor data    
    pm2p5=readings.pm_ug_per_m3(2.5,atmospheric_environment=True)
    pm1=readings.pm_ug_per_m3(1.0,atmospheric_environment=True)
    pm10=readings.pm_ug_per_m3(None,atmospheric_environment=True)
    
    s0p3= readings.pm_per_1l_air(0.3)
    s0p5= readings.pm_per_1l_air(0.5)
    s1p0= readings.pm_per_1l_air(1.0)
    s2p5= readings.pm_per_1l_air(2.5)
    s5= readings.pm_per_1l_air(5)
    s10= readings.pm_per_1l_air(10)
    
    #authenticate through json and enabling the api
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('pmssensor-3f63bc6a6dbf.json', scope)
    gc = gspread.authorize(credentials)
    #pipe data to worksheet
    wks = gc.open("PMSReadings")
    worksheet = wks.get_worksheet(0)
    next_row = next_available_row(worksheet)
    worksheet.update_acell("A{}".format(next_row), today)
    worksheet.update_acell("B{}".format(next_row), pm2p5)
    worksheet.update_acell("C{}".format(next_row), pm1)
    worksheet.update_acell("D{}".format(next_row), pm10)
    worksheet.update_acell("E{}".format(next_row), s0p3)
    worksheet.update_acell("F{}".format(next_row), s0p5)
    worksheet.update_acell("G{}".format(next_row), s1p0)
    worksheet.update_acell("H{}".format(next_row), s2p5)
    worksheet.update_acell("I{}".format(next_row), s5)
    worksheet.update_acell("J{}".format(next_row), s10)
    worksheet.update_acell("K{}".format(next_row), humidity)
    worksheet.update_acell("L{}".format(next_row), pressure)
except:
    #if failed connection to Google Docs
    MESSAGE = 'Failed to connect GDocs'
    for i in range(210):
        proximity = ltr559.get_proximity()
        if proximity > 1500:
            sys.exit(0)
        x=(time.time() - t_start) * 100
        x %= (size_x + 200)
        draw.rectangle((0, 0, 160, 80), (0, 0, 0))
        draw.text((int(text_x - x), text_y), MESSAGE, font=font, fill=(255, 255, 255))
        st7735.display(img)
        i
    sys.exit(0)

try:
    while True:
        #Display sensor data to LCD
        readings=pms5003.read()
        pm2p5=readings.pm_ug_per_m3(2.5,atmospheric_environment=True)
        pm1=readings.pm_ug_per_m3(1.0,atmospheric_environment=True)
        pm10=readings.pm_ug_per_m3(None,atmospheric_environment=True)
    
        s0p3= readings.pm_per_1l_air(0.3)
        s0p5= readings.pm_per_1l_air(0.5)
        s1p0= readings.pm_per_1l_air(1.0)
        s2p5= readings.pm_per_1l_air(2.5)
        s5= readings.pm_per_1l_air(5)
        s10= readings.pm_per_1l_air(10)
    
        msg = 'Program will continue to loop. Touch light sensor to exit'
        particles = [pm2p5, pm1, pm10, s1p0, s2p5, s10]
        description = ['pm2.5:', 'pm1:', 'pm10:', 's1.0:', 's2.5:', 's10:']
        for x in range(len(particles)):
            MESSAGE = description[x] + ' ' + str(particles[x])
            st7735 = ST7735.ST7735(port=0, cs=1, dc=9, backlight=12, rotation=270, spi_speed_hz=10000000)
            st7735.begin()
            WIDTH = st7735.width
            HEIGHT = st7735.height
            img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0 , 0))
            draw = ImageDraw.Draw(img)
            font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
            size_x, size_y = draw.textsize(MESSAGE, font)
            text_x=160
            text_y=(80 - size_y) // 2
            t_start = time.time()
            for i in range(110):
                x=(time.time() - t_start) * 100
                x %= (size_x + 200)
                draw.rectangle((0, 0, 160, 80), (0, 0, 0))
                draw.text((int(text_x - x), text_y), MESSAGE, font=font, fill=(255, 255, 255))
                st7735.display(img)
                i
        #stop loop
        MESSAGE='touch sensor to stop loop. 1 min loop'
        for t in range(1500):
            proximity = ltr559.get_proximity()
            if proximity > 1500:
                raise KeyboardInterrupt
            x=(time.time() - t_start) * 100
            x %= (size_x + 1000)
            draw.rectangle((0, 0, 160, 80), (0, 0, 0))
            draw.text((int(text_x - x), text_y), MESSAGE, font=font, fill=(255, 255, 255))
            st7735.display(img)
            t
except KeyboardInterrupt:
    #option to end the program if left alone or shutdown entire OS if light sensor is touched
    time.sleep(5)
    MESSAGE='touch sensor to shutdown; leave alone to exit program. 1 min'
    for j in range(1500):
        proximity = ltr559.get_proximity()
        if proximity > 1500:
            pms5003.reset()
            subprocess.Popen(['sudo', 'shutdown', '-h', 'now'])
        x=(time.time() - t_start) * 100
        x %= (size_x + 1000)
        draw.rectangle((0, 0, 160, 80), (0, 0, 0))
        draw.text((int(text_x - x), text_y), MESSAGE, font=font, fill=(255, 255, 255))
        st7735.display(img)
        j
    sys.exit(0)


  
