# TKinter_ACS122

 RASPBERRYPI - PYTHON 2.7 - TKinter - NFC_ACS122

 LCD [Driver](http://osoyoo.com/driver/LCD_show_35hdmi.tar.gz)
```
sudo chmod 777 LCD_show_35hdmi.tar.gz

tar -xzvf LCD_show_35hdmi.tar.gz

cd LCD_show_35hdmi

sudo apt-get update

Resolution 480*320: sudo ./LCD35_480*320
Resolution 720*480: sudo ./LCD35_720*480
Resolution 810*540: sudo ./LCD35_810*540
```
Drivers
```Terminal
sudo apt-get update

sudo apt-get install swig 
sudo apt-get install pcscd libusb-dev libpcsclite1 libpcsclite-dev dh-autoreconf

cd /opt/
sudo wget https://github.com/nfc-tools/libnfc/archive/libnfc-1.7.1.zip
sudo unzip libnfc-1.7.1.zip
cd libnfc-libnfc-1.7.1/
sudo autoreconf -vis
sudo ./configure --with-drivers=all
sudo make
sudo make install

```
Python packages
~~~Python
sudo pip install pyscard

sudo apt-get install python-imaging-tk
~~~

Autostart terminal:
In the **terminal** nano ~/.config/lxsession/LXDE-pi/autostart
add the following line :
```
'x-terminal-emulator'
```
In the **terminal**: sudo nano /home/pi/.bashrc 
add the following line :
```
sudo python2 path/main.py
```


**sebasuribe07@gmail.com**
