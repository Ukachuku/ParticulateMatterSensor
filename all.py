#!/usr/bin/python

from pms5003 import PMS5003
from pms5003 import PMS5003, ReadTimeoutError
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from time import sleep, time, localtime, strftime
import ST7735
import time
import sys
#import pyautogui
import keyboard
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



# Configure the PMS5003 for Enviro+
pms5003 = PMS5003()


out_name = 'LOG_' + strftime('%Y%m%d%H%M%S', localtime())+ '.csv'
f = open(out_name,'w')
f.write('PM1.0, PM2.5, PM10, S0.3, S0.5, S1.0, S2.5, S5, S10\n')
#need to catch the checksum error
try:
    while True:
        readings=pms5003.read()
        
        #1 minute loop to give user the chance to exit program        
        '''for t in range(1500):
            proximity = ltr559.get_proximity()
            if proximity > 1500:
                keyboard.send('ctrl+c')
            x=(time.time() - t_start) * 100
            x %= (size_x + 1000)
            draw.rectangle((0, 0, 160, 80), (0, 0, 0))
            draw.text((int(text_x - x), text_y), msg, font=font, fill=(255, 255, 255))
            st7735.display(img)
            t'''
except ReadTimeoutError:
    # Configure the PMS5003 for Enviro+
    pms5003 = PMS5003()
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
        x=(time.time() - t_start) * 100
        x %= (size_x + 200)
        draw.rectangle((0, 0, 160, 80), (0, 0, 0))
        draw.text((int(text_x - x), text_y), MESSAGE, font=font, fill=(255, 255, 255))
        st7735.display(img)
        i
    try:
        while True:
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
    
        
            f.write('{:03d},'.format(pm1))
            f.write('{:03d},'.format(pm2p5))
            f.write('{:03d},'.format(pm10))
            f.write('{:5d},'.format(s0p3))
            f.write('{:5d},'.format(s0p5))
            f.write('{:5d},'.format(s1p0))
            f.write('{:5d},'.format(s2p5))
            f.write('{:5d},'.format(s5))
            f.write('{:5d}\n'.format(s10))
        
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
                    x %= (size_x + 160)
                    draw.rectangle((0, 0, 160, 80), (0, 0, 0))
                    draw.text((int(text_x - x), text_y), MESSAGE, font=font, fill=(255, 255, 255))
                    st7735.display(img)
                    i
            MESSAGE='touch sensor to stop loop. 1 min loop'
            for t in range(1500):
                proximity = ltr559.get_proximity()
                if proximity > 1500:
                    f.close()
                    raise KeyboardInterrupt
                x=(time.time() - t_start) * 100
                x %= (size_x + 160)
                draw.rectangle((0, 0, 160, 80), (0, 0, 0))
                draw.text((int(text_x - x), text_y), MESSAGE, font=font, fill=(255, 255, 255))
                st7735.display(img)
                t
    except KeyboardInterrupt:
        MESSAGE='touch sensor to shutdown; leave alone to exit program. 1 min'
        for j in range(1500):
            proximity = ltr559.get_proximity()
            if proximity > 1500:
                subprocess.Popen(['sudo', 'shutdown', '-h', 'now'])
            x=(time.time() - t_start) * 100
            x %= (size_x + 1000)
            draw.rectangle((0, 0, 160, 80), (0, 0, 0))
            draw.text((int(text_x - x), text_y), MESSAGE, font=font, fill=(255, 255, 255))
            st7735.display(img)
            j
        sys.exit(0)
