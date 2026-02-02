from machine import Pin,I2C
import time
import network
import urequests
from sh1106 import SH1106_I2C
from dht import DHT11
from micropython import const


i2c = I2C(1, sda = Pin(2), scl=Pin(3), freq = 40000) #both the i2c bus and oled variables are shared resources
oled = SH1106_I2C(128, 64, i2c)



wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect('****', '****')

while (wifi.isconnected() == False):
    print('Waiting for Connection . . . .')
    time.sleep(1)

print("Congratulations, You have Connected!")
wifiInfo = wifi.ifconfig()
print(wifiInfo)

weather = urequests.get("https://api.openweathermap.org/data/2.5/weather?q=Vaughan,Canada&appid=263474b42dfd6a8eb1602dbf16346cd1").json()

print(weather)
pressure = weather['main']['pressure'] / 10
temp = weather['main']['temp'] - 273.15
humidity = weather['main']['humidity']


datapin = Pin(16, Pin.OUT, Pin.PULL_DOWN) #read the data from GPIO 16
sensor = DHT11(datapin)

#initial readings
tempC = sensor.temperature()
hum = sensor.humidity()


myButton = Pin(15, Pin.IN, Pin.PULL_UP)
previous = myButton.value()
x = 0
while x > -50:
        oled.fill(0)
        oled.text("Location: " + str(weather['name']) +',' + str(weather['sys']['country']), x,0)
        oled.text("Humidity: "+ str(humidity) + "%", 0, 9)
        oled.text("Temp: " + str(round(temp,2)) + 'C' , 0,18)
        oled.text("Pressure: " + str(pressure) +"kPa", x,27)
        oled.text(" Sensor Data:", 0,38)
     
        if (myButton.value() != previous): #if you press the button it takes a reading from the temperature sensor
            sensor.measure()
            tempC = sensor.temperature()
            hum = sensor.humidity()
        oled.text(" ->Temp: " + str(tempC) + 'C', 0,47)
        oled.text(" ->Humidity: " + str(hum) + '%',0,56)
        oled.show()
        
        x = x - 1
        if (x <= -50): #reset the counter when it gets below a certain value
            x = 0


def othercore():
    core_lock.acquire()
    datapin = Pin(16, Pin.OUT, Pin.PULL_DOWN) #read the data from GPIO 16
    sensor = DHT11(datapin)
    while True:
        sensor.measure() #does not return anything
        tempC = sensor.temperature()
        hum = sensor.humidity()
        print("\r", 'Current Temperature = ', tempC, chr(176) +'C ', 'Current Humidity = ', hum, '%', end = '') #/r overwrites the print statement with a new print statement
        oled.text("Sensor Temp: " + str(tempC), 0, 45)
        time.sleep(4) # doesn't work very well if you don't add a delay
        core_lock.release()
