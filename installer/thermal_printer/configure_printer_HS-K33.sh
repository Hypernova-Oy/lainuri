#!/bin/bash

cd $(dirname $0)

echo "1. Make sure CUPS is installed"
sudo apt install -y cups

echo "2. Deploy the driver"
sudo cp rastertopos /usr/lib/cups/filter/
sudo chmod 755 /usr/lib/cups/filter/rastertopos
sudo chown root:root /usr/lib/cups/filter/rastertopos
sudo cp pos80.ppd /usr/lib/cups/driver/pos80.ppd
sudo chmod 644 /usr/lib/cups/driver/pos80.ppd
sudo chown root:root /usr/lib/cups/driver/pos80.ppd

echo "3. Adding a system CUPS printer"
PRINTER_URL=$(sudo lpinfo -v | grep -P '^direct' | grep -Po 'usb://Unknown/Printer\?serial=(.+)$')
test -z $PRINTER_URL && \
  echo "Couldn't find the printer with lpinfo! Is the printer plugged in directly to the Raspberry Pi and identified as a USB-device?" && \
  exit 10

sudo lpadmin -p HS-K33 -P /usr/lib/cups/driver/pos80.ppd -u allow:all -E -v "$PRINTER_URL"

# Configure as system default printer, with feed and half cut + buzzer
sudo lpoptions -p HS-K33 -o OptionCutPaperAfterPage=1 -o OptionBuzzingAfterPage=1 -o PageSize=72mmx100mm
sudo lpoptions -d HS-K33

echo "4. Print test page"
lp /usr/share/cups/data/testprint
if [ $? != 0 ]; then
  echo "Printing CUPS test page failed!"
  # TODO: message zabbix of failure notifications
  exit 10
fi


