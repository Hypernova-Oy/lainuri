#!/bin/bash

echo "1. Unarchiving the vendor CUPS driver"
# Encrypting the vendor SDK, Docs, and Driver to prevent leaking confidential information to version control.
#gpg --batch --no-tty --yes --passphrase-file ../../installer_secret_passphrase --encrypt -o HS-K33.tar.gz.gpg HS-K33.tar.gz
gpg --batch --no-tty --yes --passphrase-file ../../installer_secret_passphrase --decrypt -o HS-K33.tar.gz HS-K33.tar.gz.gpg
tar -xzf HS-K33.tar.gz

echo "2. Deploy the driver"
sudo cp HS-K33/Drivers/Linux/filter/64/rastertopos /usr/lib/cups/filter/
chmod a+x /usr/lib/cups/filter/rastertopos
sudo cp HS-K33/Drivers/Linux/ppd/pos80.ppd /usr/lib/cups/driver/pos80.ppd

echo "3. Adding a system CUPS printer"
PRINTER_URL=$(lpinfo -v | grep -P '^direct' | grep -Po 'usb://Unknown/Printer\?serial=(.+)$')
lpadmin -p HS-K33 -P /usr/lib/cups/driver/pos80.ppd -u allow:all -E -v usb://Unknown/Printer?serial=002F00420238AB3900000ECC
# Configure as system default printer, with feed and half cut + buzzer
lpoptions -p HS-K33 -o OptionCutPaperAfterPage=1 -o OptionBuzzingAfterPage=1 -o PageSize=72mmx100mm
lpoptions -d HS-K33

echo "4. Print test page"
lp /usr/share/cups/data/testprint
if [ $? != 0 ]; then
  echo "Printing CUPS test page failed!"
  # TODO: message zabbix of failure notifications
  exit 10
fi
