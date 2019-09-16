# TKinter_ACS122

 RASPBERRYPI - PYTHON 2.7 - TKinter - NFC_ACS122

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

```Python
sudo pip install pyscard

sudo apt-get install python-imaging-tk
```

**sebasuribe07@gmail.com**
