EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "Lainuri"
Date ""
Rev ""
Comp "Hypernova Oy"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Koha-Suomi:Barcode_Reader BCR1
U 1 1 5EB915D4
P 8350 500
F 0 "BCR1" H 8300 450 50  0000 L CNN
F 1 "Barcode_Reader" H 8100 100 50  0000 L CNN
F 2 "" H 8350 500 50  0001 C CNN
F 3 "" H 8350 500 50  0001 C CNN
F 4 "WGI3220USB" H 8350 500 50  0001 C CNN "Model"
F 5 "WinsonChina" H 8350 500 50  0001 C CNN "Vendor"
F 6 "44.78" H 8350 500 50  0001 C CNN "ALV0%€"
	1    8350 500 
	1    0    0    -1  
$EndComp
$Comp
L Koha-Suomi:RFID_readerwriter RFID_RW1
U 1 1 5EB9DA51
P 6950 1650
F 0 "RFID_RW1" H 6800 1950 50  0000 L CNN
F 1 "RFID_readerwriter" H 6550 1350 50  0000 L CNN
F 2 "" H 6950 1650 50  0001 C CNN
F 3 "" H 6950 1650 50  0001 C CNN
F 4 "RL866" H 6950 1650 50  0001 C CNN "Model"
F 5 "Guangzhou Andea" H 6950 1650 50  0001 C CNN "Vendor"
F 6 "56.65" H 6950 1650 50  0001 C CNN "ALV0%€"
	1    6950 1650
	-1   0    0    -1  
$EndComp
Text Notes 15150 3650 0    60   ~ 0
Door relay
Text Notes 14150 3550 0    60   ~ 0
PCB DOOR
$Comp
L authenticator-rescue:AST-1732MR-R AST1
U 1 1 59892846
P 7200 3450
F 0 "AST1" H 6900 3050 60  0000 C CNN
F 1 "AST-1732MR-R" H 6900 3450 60  0000 C CNN
F 2 "Koha-Suomi:AST-1732MR-R" H 7200 3450 60  0001 C CNN
F 3 "https://www.mouser.fi/datasheet/2/334/AST-1732MR-R-72511.pdf" H 7200 3450 60  0001 C CNN
F 4 "AST-1732MR-R" H 7200 3450 50  0001 C CNN "Model"
F 5 "Speakers & Transducers SPEAKER 32OHM" H 7200 3450 50  0001 C CNN "Title"
F 6 "PUI Audio" H 7200 3450 50  0001 C CNN "Manufacturer"
F 7 "3.50" H 7200 3450 50  0001 C CNN "ALV0%€"
	1    7200 3450
	-1   0    0    -1  
$EndComp
$Comp
L authenticator-rescue:D D1
U 1 1 5C0CCD9B
P 14300 3850
F 0 "D1" H 14300 3950 50  0000 C CNN
F 1 "D" H 14300 3750 50  0000 C CNN
F 2 "Koha-Suomi:1N4154TAP" H 14300 3850 50  0001 C CNN
F 3 "https://www.mouser.fi/datasheet/2/427/1n4154-241332.pdf" H 14300 3850 50  0001 C CNN
F 4 "1N4154TAP" H 14300 3850 50  0001 C CNN "Model"
F 5 "Diodes - General Purpose, Power, Switching Vr/35v Io/150mA" H 14300 3850 50  0001 C CNN "Title"
F 6 "Vishay Semiconductors" H 14300 3850 50  0001 C CNN "Manufacturer"
F 7 "0.135" H 14300 3850 50  0001 C CNN "ALV0%€"
	1    14300 3850
	-1   0    0    -1  
$EndComp
$Comp
L authenticator-rescue:D D2
U 1 1 5C0CD021
P 14300 4850
F 0 "D2" H 14300 4950 50  0000 C CNN
F 1 "D" H 14300 4750 50  0000 C CNN
F 2 "Koha-Suomi:1N4154TAP" H 14300 4850 50  0001 C CNN
F 3 "https://www.mouser.fi/datasheet/2/427/1n4154-241332.pdf" H 14300 4850 50  0001 C CNN
F 4 "1N4154TAP" H 14300 4850 50  0001 C CNN "Model"
F 5 "Diodes - General Purpose, Power, Switching Vr/35v Io/150mA" H 14300 4850 50  0001 C CNN "Title"
F 6 "Vishay Semiconductors" H 14300 4850 50  0001 C CNN "Manufacturer"
F 7 "0.135" H 14300 4850 50  0001 C CNN "ALV0%€"
	1    14300 4850
	-1   0    0    -1  
$EndComp
NoConn ~ 14200 4400
NoConn ~ 14200 4300
Wire Notes Line
	14750 3650 15850 3650
Wire Notes Line
	15850 3450 13850 3450
Wire Notes Line
	13850 3450 13850 5200
Wire Wire Line
	14450 3850 15100 3850
Wire Wire Line
	14450 4850 15100 4850
Wire Wire Line
	15100 4850 15100 4600
Wire Wire Line
	14100 4500 15200 4500
Wire Wire Line
	14100 3850 14100 4100
Wire Wire Line
	14100 4600 14200 4600
Connection ~ 14100 4600
Wire Wire Line
	14100 4850 14150 4850
Wire Wire Line
	14150 3850 14100 3850
Wire Wire Line
	14100 4100 14200 4100
Connection ~ 14100 4500
Connection ~ 14100 4100
Wire Wire Line
	15100 3850 15100 4100
Text Notes 14400 5150 0    61   ~ 0
Electric lock\nnormal open\n
Connection ~ 15100 3850
Text Label 15150 3850 0    61   ~ 0
PiHat_35_doorOFF
Connection ~ 15100 4850
Text Label 15100 4950 0    61   ~ 0
PiHat_37_doorON
Text Label 15200 4800 0    61   ~ 0
PiHat_39_doorGND
NoConn ~ 14200 4200
NoConn ~ 15100 4400
Wire Wire Line
	14100 4600 14100 4850
Wire Wire Line
	14100 4500 14100 4600
Wire Wire Line
	14100 4100 14100 4500
Wire Wire Line
	15100 3850 15150 3850
Wire Wire Line
	15100 4850 15100 4950
Wire Notes Line
	13850 3550 15850 3550
$Comp
L authenticator-rescue:Cat-cable-Koha-Suomi CAT1
U 1 1 5D3638A4
P 5600 2450
F 0 "CAT1" H 5150 2350 50  0000 C CNN
F 1 "Cat-cable" H 5600 2650 50  0000 C CNN
F 2 "Koha-Suomi:Bad_board_tag" V 5600 2475 50  0001 C CNN
F 3 "~" V 5600 2475 50  0001 C CNN
F 4 "5m" H 5300 2650 50  0000 C CNN "Length"
F 5 "557-345" H 5600 2450 50  0001 C CNN "Model"
F 6 "RS Pro Red Cat6 Cable F/UTP LSZH, 5m" H 5600 2450 50  0001 C CNN "Title"
F 7 "fi.rsdelivers.com" H 5600 2450 50  0001 C CNN "Supplier"
F 8 "RS PRO" H 5600 2450 50  0001 C CNN "Manufacturer"
F 9 "9.80" H 5600 2450 50  0001 C CNN "ALV0%€"
	1    5600 2450
	0    1    1    0   
$EndComp
$Comp
L authenticator-rescue:RPi_GPIO-Koha-Suomi RPi1
U 1 1 57BB6E59
P 5150 3100
F 0 "RPi1" H 6500 1100 60  0000 C CNN
F 1 "RPi_GPIO" H 5350 1100 60  0000 C CNN
F 2 "Koha-Suomi:PI_GPIO_Header_F_2x20" H 5150 3100 60  0001 C CNN
F 3 "" H 5150 3100 60  0001 C CNN
F 4 "" H 5150 3100 50  0001 C CNN "Model"
F 5 "40 Pin Extra Tall Header (Push Fit Version)" H 5150 3100 50  0001 C CNN "Title"
F 6 "Adafruit" H 5150 3100 50  0001 C CNN "Manufacturer"
F 7 "thepihut.com" H 5150 3100 50  0001 C CNN "Supplier"
F 8 "13.5mm" H 5150 3100 50  0001 C CNN "BodyHeight"
F 9 "2.27" H 5150 3100 50  0001 C CNN "ALV0%€"
	1    5150 3100
	1    0    0    -1  
$EndComp
Wire Wire Line
	15200 4500 15200 4800
Wire Wire Line
	15100 4200 15200 4200
Wire Wire Line
	15100 4300 15200 4300
$Comp
L Switch:SW_Push_LED SW1
U 1 1 5D6814C3
P 7400 4250
F 0 "SW1" H 7400 4500 50  0000 C CNN
F 1 "SW_Push_LED" H 7400 4100 50  0000 C CNN
F 2 "Connectors_Molex:Molex_KK-6410-04_04x2.54mm_Straight" H 7400 4550 50  0001 C CNN
F 3 "" H 7400 4550 50  0001 C CNN
F 4 "ADA1439" H 7400 4250 50  0001 C CNN "Model"
F 5 "16mm Illuminated Pushbutton - Red Momentary" H 7400 4250 50  0001 C CNN "Title"
F 6 "thepihut.com" H 7400 4250 50  0001 C CNN "Vendor"
F 7 "1.70" H 7400 4250 50  0001 C CNN "ALV0%€"
	1    7400 4250
	-1   0    0    -1  
$EndComp
$Comp
L authenticator-rescue:SoC-Koha-Suomi SOC1
U 1 1 5D33119C
P 10150 800
F 0 "SOC1" H 10050 700 50  0000 L CNN
F 1 "SoC" H 10050 1000 50  0000 L CNN
F 2 "Koha-Suomi:Bad_board_tag" H 10150 800 50  0001 C CNN
F 3 "https://thepihut.com/products/raspberry-pi-4-model-b?variant=20064052740158" H 10150 800 50  0001 C CNN
F 4 "Raspberry Pi 4 Model B" H 10150 800 50  0001 C CNN "Model"
F 5 "Raspberry Pi" H 10150 800 50  0001 C CNN "Manufacturer"
F 6 "https://thepihut.com" H 10150 800 50  0001 C CNN "Supplier"
F 7 "Raspberry Pi 4 Model B" H 10150 800 50  0001 C CNN "Title"
F 8 "61.22" H 10150 800 50  0001 C CNN "ALV0%€"
	1    10150 800 
	1    0    0    -1  
$EndComp
$Comp
L authenticator-rescue:SD_Card-Koha-Suomi SD1
U 1 1 5D333748
P 10450 850
F 0 "SD1" H 10400 800 50  0000 L CNN
F 1 "SD_Card" H 10350 1050 50  0000 L CNN
F 2 "Koha-Suomi:Bad_board_tag" H 10450 850 50  0001 C CNN
F 3 "" H 10450 850 50  0001 C CNN
F 4 "NOOBS_32GB_Retail" H 10450 850 50  0001 C CNN "Model"
F 5 "SD Card preloaded with NOOBS - 32GB" H 10450 850 50  0001 C CNN "Title"
F 6 "fi.rsdelivers.com" H 10450 850 50  0001 C CNN "Supplier"
F 7 "Raspberry Pi" H 10450 850 50  0001 C CNN "Manufacturer"
F 8 "12" H 10450 850 50  0001 C CNN "ALV0%€"
	1    10450 850 
	1    0    0    -1  
$EndComp
$Comp
L authenticator-rescue:RPi_Enclosure-Koha-Suomi RPE1
U 1 1 5D336DF3
P 10900 1400
F 0 "RPE1" H 10750 1600 50  0000 L CNN
F 1 "RPi_Enclosure" H 10650 1250 50  0000 L CNN
F 2 "Koha-Suomi:Bad_board_tag" H 10900 1400 50  0001 C CNN
F 3 "https://thepihut.com/collections/featured-products/products/aluminium-armour-heatsink-case-for-raspberry-pi-4" H 10900 1400 50  0001 C CNN
F 4 "TPH-002" H 10900 1400 50  0001 C CNN "Model"
F 5 "Aluminium Armour - Heatsink Case for Raspberry Pi 4" H 10900 1400 50  0001 C CNN "Title"
F 6 "" H 10900 1400 50  0001 C CNN "Manufacturer"
F 7 "https://thepihut.com" H 10900 1400 50  0001 C CNN "Supplier"
F 8 "13.60" H 10900 1400 50  0001 C CNN "ALV0%€"
	1    10900 1400
	1    0    0    -1  
$EndComp
$Comp
L authenticator-rescue:USB-Stick-Koha-Suomi US1
U 1 1 5D338938
P 10250 1400
F 0 "US1" H 10200 1550 50  0000 L CNN
F 1 "USB-Stick" H 10100 1250 50  0000 L CNN
F 2 "" H 10250 1400 50  0001 C CNN
F 3 "" H 10250 1400 50  0001 C CNN
F 4 "THN-U401S0320E4" H 10250 1400 50  0001 C CNN "Model"
F 5 "Toshiba 32GB TransMemory USB2.0 Metal" H 10250 1400 50  0001 C CNN "Title"
F 6 "Toshiba" H 10250 1400 50  0001 C CNN "Manufacturer"
F 7 "fi.rsdelivers.com" H 10250 1400 50  0001 C CNN "Supplier"
F 8 "17.20" H 10250 1400 50  0001 C CNN "ALV0%€"
	1    10250 1400
	1    0    0    -1  
$EndComp
$Comp
L authenticator-rescue:Cable_USB_TypeA_F_M-Koha-Suomi HDMI1
U 1 1 5D34BCD9
P 9950 2000
F 0 "HDMI1" H 9850 2050 50  0000 C CNN
F 1 "Cable_HDMI-mini_to_HDMI (Raspi to touch screen)" H 10100 2150 50  0000 C CNN
F 2 "" H 9950 2000 50  0001 C CNN
F 3 "https://thepihut.com/products/diy-usb-or-hdmi-cable-parts-10-cm-ribbon-cable" H 9950 2000 50  0001 C CNN
F 4 "ADA3560" H 9950 2000 50  0001 C CNN "Model"
F 5 "" H 9950 2000 50  0001 C CNN "Manufacturer"
F 6 "DIY USB or HDMI Cable Parts - 10 cm Ribbon Cable" H 9950 2000 50  0001 C CNN "Title"
F 7 "thepihut.com" H 9950 2000 50  0001 C CNN "Supplier"
F 8 "1.70" H 9950 2000 50  0001 C CNN "ALV0%€"
F 9 "0.1m" H 10050 1950 50  0000 C CNN "Length"
	1    9950 2000
	1    0    0    -1  
$EndComp
$Comp
L Mechanical:Housing N2
U 1 1 5F1B1EB0
P 9800 800
F 0 "N2" H 9700 1000 50  0000 L CNN
F 1 "External enclosure" H 9350 550 50  0000 L CNN
F 2 "" H 9850 850 50  0001 C CNN
F 3 "" H 9850 850 50  0001 C CNN
F 4 "" H 9800 800 50  0001 C CNN "Model"
F 5 "Laser cut enclosure sheets that are glued together. Price varies based on customer needs." H 9800 800 50  0001 C CNN "Title"
F 6 "cotter.co" H 9800 800 50  0001 C CNN "Manufacturer"
F 7 "200" H 9800 800 50  0001 C CNN "ALV0%€"
	1    9800 800 
	1    0    0    -1  
$EndComp
$Comp
L Connector:Screw_Terminal_01x02 T2
U 1 1 5D4DF08C
P 15400 4200
F 0 "T2" H 15500 4150 50  0000 C CNN
F 1 "Screw_Terminal_01x02" H 15550 4300 50  0000 C CNN
F 2 "Koha-Suomi:Screw_Terminal_01x02 (Molex)" H 15400 4200 50  0001 C CNN
F 3 "https://www.mouser.fi/datasheet/2/276/0398800302_TERMINAL_BLOCKS-167600.pdf" H 15400 4200 50  0001 C CNN
F 4 "39880-0302" H 15400 4200 50  0001 C CNN "Model"
F 5 "Fixed Terminal Blocks 2 CKT TERM. BLOCK 5.08mm" H 15400 4200 50  0001 C CNN "Title"
F 6 "Molex" H 15400 4200 50  0001 C CNN "Manufacturer"
F 7 "0.648" H 15400 4200 50  0001 C CNN "ALV0%€"
	1    15400 4200
	1    0    0    -1  
$EndComp
$Comp
L authenticator-rescue:EC2-3TNU EC2
U 1 1 5C0CC6F5
P 14400 4900
F 0 "EC2" V 15350 4650 60  0000 C CNN
F 1 "EC2-3TNU" V 14550 4650 60  0000 C CNN
F 2 "Koha-Suomi:EC2-3TNU" H 14400 4900 60  0001 C CNN
F 3 "https://www.mouser.fi/datasheet/2/212/KEM_R7002_EC2_EE2-1104574.pdf" H 14400 4900 60  0001 C CNN
F 4 "EC2-3TNU" H 14400 4900 50  0001 C CNN "Model"
F 5 "Low Signal Relays - PCB 3V 2A Dbl Latching LL=3.2mm" H 14400 4900 50  0001 C CNN "Title"
F 6 "KEMET" V 14400 4900 50  0001 C CNN "Manufacturer"
F 7 "2.42" V 14400 4900 50  0001 C CNN "ALV0%€"
	1    14400 4900
	0    -1   -1   0   
$EndComp
$Comp
L Koha-Suomi:Touch_screen TSCR1
U 1 1 5ED1A0D7
P 7050 2550
F 0 "TSCR1" H 6950 2900 50  0000 L CNN
F 1 "Touch_screen" H 6800 2200 50  0000 L CNN
F 2 "" H 7050 2550 50  0001 C CNN
F 3 "" H 7050 2550 50  0001 C CNN
F 4 "13.3 inch capacitive touch screen monitor 1920*1080 wit" H 7050 2550 50  0001 C CNN "Title"
F 5 "GC1316" H 7050 2550 50  0001 C CNN "Model"
F 6 "126.36" H 7050 2550 50  0001 C CNN "ALV0%€"
	1    7050 2550
	-1   0    0    -1  
$EndComp
$Comp
L Koha-Suomi:USB_Hub_4port UHUB1
U 1 1 5ED2A4DD
P 8300 2550
F 0 "UHUB1" H 8200 2900 50  0000 L CNN
F 1 "USB_Hub_4port" H 8050 2300 50  0000 L CNN
F 2 "" H 8450 2500 50  0001 C CNN
F 3 " ~" H 8450 2500 50  0001 C CNN
F 4 "Ultra thin 4 Ports usb 3.0 Splitter Hub with DC Power Interface f" H 8300 2550 50  0001 C CNN "Title"
F 5 "" H 8300 2550 50  0001 C CNN "Model"
F 6 "Shenzhen Lcr Industries" H 8300 2550 50  0001 C CNN "Vendor"
F 7 "10.00" H 8300 2550 50  0001 C CNN "ALV0%€"
	1    8300 2550
	1    0    0    -1  
$EndComp
$Comp
L power:+24V #PWR0101
U 1 1 5ED40728
P 4000 900
F 0 "#PWR0101" H 4000 750 50  0001 C CNN
F 1 "+24V" H 4015 1073 50  0000 C CNN
F 2 "" H 4000 900 50  0001 C CNN
F 3 "" H 4000 900 50  0001 C CNN
F 4 "ORIGINAL Meanwell GST160A24-R7B 160W" H 4015 1164 50  0001 C CNN "Title"
F 5 "GST160A24-R7B" H 3900 1150 50  0000 C CNN "Model"
F 6 "Yiwu Yuezi Import and Export Co" H 4000 900 50  0001 C CNN "Vendor"
F 7 "27.23" H 4000 900 50  0001 C CNN "ALV0%€"
	1    4000 900 
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR0102
U 1 1 5ED41E26
P 4000 1100
F 0 "#PWR0102" H 4000 850 50  0001 C CNN
F 1 "GND" H 4005 927 50  0000 C CNN
F 2 "" H 4000 1100 50  0001 C CNN
F 3 "" H 4000 1100 50  0001 C CNN
	1    4000 1100
	0    1    1    0   
$EndComp
$Comp
L Koha-Suomi:Step_converter SC1
U 1 1 5ED60F64
P 4650 1550
F 0 "SC1" H 4400 1850 50  0000 C CNN
F 1 "Step_down_24V-12VA2" H 4600 1350 50  0000 C CNN
F 2 "" H 4650 1550 50  0001 C CNN
F 3 "" H 4650 1550 50  0001 C CNN
F 4 "Step down regulator 24v to 12v 3a step down dc dc converter" H 4650 1550 50  0001 C CNN "Title"
F 5 "Yucoo Network Equipment Co" H 4650 1550 50  0001 C CNN "Vendor"
F 6 "3.52" H 4650 1550 50  0001 C CNN "ALV0%€"
	1    4650 1550
	1    0    0    -1  
$EndComp
$Comp
L Koha-Suomi:Step_converter SC2
U 1 1 5ED64079
P 4650 2450
F 0 "SC2" H 4400 2750 50  0000 C CNN
F 1 "Step_down_24V-5VA3.1" H 4600 2250 50  0000 C CNN
F 2 "" H 4650 2450 50  0001 C CNN
F 3 "" H 4650 2450 50  0001 C CNN
F 4 "Step down regulator 24v to 5v 3.1a step down dc dc converter" H 4650 2450 50  0001 C CNN "Title"
F 5 "Yucoo Network Equipment Co" H 4650 2450 50  0001 C CNN "Vendor"
F 6 "3.52" H 4650 2450 50  0001 C CNN "ALV0%€"
	1    4650 2450
	1    0    0    -1  
$EndComp
$Comp
L Koha-Suomi:HEADER_S_1X02 H1
U 1 1 5ED8CABE
P 4850 3000
F 0 "H1" V 4700 2500 50  0000 L CNN
F 1 "HEADER_S_1X02" V 4700 2650 50  0000 L CNN
F 2 "" H 4850 3000 50  0001 C CNN
F 3 "https://www.mouser.fi/datasheet/2/276/1/0687980010_CABLE_ASSEMBLIES-1315736.pdf" H 4850 3000 50  0001 C CNN
F 4 "Raspberry USB-C PSU Cable" V 4800 2150 50  0000 L CNN "Title"
F 5 "68798-0010 " V 4850 3000 50  0001 C CNN "Model"
F 6 "www.mouser.fi" V 4850 3000 50  0001 C CNN "Vendor"
F 7 "6.78" V 4850 3000 50  0001 C CNN "ALV0%€"
F 8 "Molex" V 4850 3000 50  0001 C CNN "Manufacturer"
	1    4850 3000
	0    1    1    0   
$EndComp
$Comp
L Koha-Suomi:Thermal_printer THPR1
U 1 1 5EB9ADBF
P 6850 850
F 0 "THPR1" V 6850 500 50  0000 L CNN
F 1 "Thermal_printer" V 7200 400 50  0000 L CNN
F 2 "" H 6950 850 50  0001 C CNN
F 3 "" H 6950 850 50  0001 C CNN
F 4 "HS-K33" H 6850 850 50  0001 C CNN "Model"
F 5 "HSPOS TECHNOLOGY LIMITED" H 6850 850 50  0001 C CNN "Vendor"
F 6 "63.96" H 6850 850 50  0001 C CNN "ALV0%€"
	1    6850 850 
	0    -1   1    0   
$EndComp
Wire Wire Line
	4900 2450 5200 2450
Wire Wire Line
	5200 2450 5200 2800
Wire Wire Line
	4900 2350 5300 2350
Wire Wire Line
	5300 2350 5300 2800
Wire Wire Line
	4000 1100 4100 1100
Wire Wire Line
	4100 1100 4100 1650
Wire Wire Line
	4100 2550 4300 2550
Wire Wire Line
	4000 900  4200 900 
Wire Wire Line
	4200 900  4200 1000
Wire Wire Line
	4200 2250 4300 2250
Wire Wire Line
	4300 1650 4100 1650
Connection ~ 4100 1650
Wire Wire Line
	4100 1650 4100 2550
Wire Wire Line
	4300 1350 4200 1350
Connection ~ 4200 1350
Wire Wire Line
	4200 1350 4200 2250
Wire Wire Line
	4100 1100 6600 1100
Connection ~ 4100 1100
Wire Wire Line
	4200 1000 6600 1000
Connection ~ 4200 1000
Wire Wire Line
	4200 1000 4200 1350
Wire Wire Line
	4900 1450 6500 1450
Wire Wire Line
	4900 1550 6400 1550
Wire Wire Line
	6600 2400 6500 2400
Wire Wire Line
	6500 2400 6500 1450
Connection ~ 6500 1450
Wire Wire Line
	6500 1450 6600 1450
Wire Wire Line
	6400 1550 6400 2500
Wire Wire Line
	6400 2500 6600 2500
Connection ~ 6400 1550
Wire Wire Line
	6400 1550 6600 1550
Text Notes 8000 1750 0    66   ~ 13
USB to Raspberry
Wire Notes Line
	7200 1700 8000 1700
Wire Notes Line
	7400 2250 8050 2250
Wire Notes Line
	8050 2250 8050 1750
Wire Notes Line
	7100 1050 8050 1050
Wire Notes Line
	8050 1050 8050 1650
Wire Notes Line
	8350 850  8350 1650
Wire Notes Line
	8000 1650 8900 1650
Wire Notes Line
	8900 1650 8900 1750
Wire Notes Line
	8900 1750 8000 1750
Wire Notes Line
	8000 1750 8000 1650
Wire Notes Line
	7950 1600 7950 1800
Wire Notes Line
	7950 1800 8950 1800
Wire Notes Line
	8950 1800 8950 1600
Wire Notes Line
	8950 1600 7950 1600
Wire Notes Line
	8500 2250 8500 1800
Text Notes 8000 3000 0    50   ~ 0
Connect mouse and\nkeyboard etc. here
$Comp
L Mechanical:Housing N3
U 1 1 5F237B60
P 10900 800
F 0 "N3" H 10800 900 50  0000 L CNN
F 1 "PCB mnfcture" H 10650 550 50  0000 L CNN
F 2 "" H 10950 850 50  0001 C CNN
F 3 "" H 10950 850 50  0001 C CNN
F 4 "" H 10900 800 50  0001 C CNN "Model"
F 5 "PCB printing and shipping (constant R&D no batch orders)" H 10900 800 50  0001 C CNN "Title"
F 6 "allpcb.com" H 10900 800 50  0001 C CNN "Manufacturer"
F 7 "20" H 10900 800 50  0001 C CNN "ALV0%€"
	1    10900 800 
	1    0    0    -1  
$EndComp
Wire Wire Line
	7200 3600 6800 3600
Wire Wire Line
	6800 3700 7200 3700
Wire Wire Line
	7200 4250 7200 4200
Wire Wire Line
	6800 3800 7100 3800
Wire Wire Line
	7100 3800 7100 4200
Wire Wire Line
	7100 4200 7200 4200
Connection ~ 7200 4200
Wire Wire Line
	7200 4200 7200 4150
Wire Wire Line
	7600 4150 7600 4200
Wire Wire Line
	6800 3900 7700 3900
Wire Wire Line
	7700 3900 7700 4200
Wire Wire Line
	7700 4200 7600 4200
Connection ~ 7600 4200
Wire Wire Line
	7600 4200 7600 4250
$Comp
L Koha-Suomi:Part HDMI1.1
U 1 1 5EF1862E
P 9450 2000
F 0 "HDMI1.1" H 9250 2000 50  0000 L CNN
F 1 "DIY HDMI Head" H 9200 1850 50  0000 L CNN
F 2 "" H 9450 2000 50  0001 C CNN
F 3 "" H 9450 2000 50  0001 C CNN
F 4 "DIY HDMI Cable Parts - Right Angle (R bend) HDMI Plug Adapter" H 9450 2000 50  0001 C CNN "Title"
F 5 "ADA3549" H 9450 2000 50  0001 C CNN "Model"
F 6 "thepihut.com" H 9450 2000 50  0001 C CNN "Vendor"
F 7 "6.80" H 9450 2000 50  0001 C CNN "ALV0%€"
	1    9450 2000
	1    0    0    -1  
$EndComp
$Comp
L Koha-Suomi:Part HDMI1.2
U 1 1 5EF1A1EA
P 10450 2000
F 0 "HDMI1.2" H 10350 2000 50  0000 L CNN
F 1 "DIY HDMI Head" H 10200 1850 50  0000 L CNN
F 2 "" H 10450 2000 50  0001 C CNN
F 3 "" H 10450 2000 50  0001 C CNN
F 4 "DIY HDMI Cable Parts - Left Angle (L Bend) Micro HDMI Plug" H 10450 2000 50  0001 C CNN "Title"
F 5 "ADA3558" H 10450 2000 50  0001 C CNN "Model"
F 6 "thepihut.com" H 10450 2000 50  0001 C CNN "Vendor"
F 7 "6.80" H 10450 2000 50  0001 C CNN "ALV0%€"
F 8 "DIY HDMI Cable Parts - Straight Micro HDMI Plug Adapter (ADA3556)" H 10450 2000 50  0001 C CNN "Alternative model"
	1    10450 2000
	1    0    0    -1  
$EndComp
$Comp
L Koha-Suomi:Part RS_USB1
U 1 1 5EF2CE37
P 7550 1650
F 0 "RS_USB1" H 7350 1650 50  0000 L CNN
F 1 "RS-232-adapter" H 7300 1500 50  0000 L CNN
F 2 "" H 7550 1650 50  0001 C CNN
F 3 "" H 7550 1650 50  0001 C CNN
F 4 "USB/Serial Converter" H 7550 1650 50  0001 C CNN "Title"
F 5 "ADA18" H 7550 1650 50  0001 C CNN "Model"
F 6 "thepihut.com" H 7550 1650 50  0001 C CNN "Vendor"
F 7 "15.87" H 7550 1650 50  0001 C CNN "ALV0%€"
	1    7550 1650
	1    0    0    -1  
$EndComp
$Comp
L Mechanical:Heatsink HS2
U 1 1 5EF5795B
P 4650 2200
F 0 "HS2" H 4800 2350 50  0000 L CNN
F 1 "Heatsink" H 4500 2250 50  0000 L CNN
F 2 "" H 4662 2200 50  0001 C CNN
F 3 "https://fi.rsdelivers.com/product/abl-components/bga-std-090/heatsink-10k-w-239-x-40-x-10mm-adhesive-foil/7500932" H 4662 2200 50  0001 C CNN
F 4 "fi.rsdelivers.com" H 4650 2200 50  0001 C CNN "Vendor"
F 5 "BGA STD 090" H 4650 2200 50  0001 C CNN "Model"
F 6 " ABL Components" H 4650 2200 50  0001 C CNN "Manufacturer"
F 7 "1.90" H 4650 2200 50  0001 C CNN "ALV0%€"
	1    4650 2200
	1    0    0    -1  
$EndComp
$Comp
L Mechanical:Heatsink HS1
U 1 1 5EF5995C
P 4650 1300
F 0 "HS1" H 4800 1400 50  0000 L CNN
F 1 "Heatsink" H 4500 1350 50  0000 L CNN
F 2 "" H 4662 1300 50  0001 C CNN
F 3 "https://fi.rsdelivers.com/product/abl-components/bga-std-090/heatsink-10k-w-239-x-40-x-10mm-adhesive-foil/7500932" H 4662 1300 50  0001 C CNN
F 4 "fi.rsdelivers.com" H 4650 1300 50  0001 C CNN "Vendor"
F 5 "BGA STD 090" H 4650 1300 50  0001 C CNN "Model"
F 6 " ABL Components" H 4650 1300 50  0001 C CNN "Manufacturer"
F 7 "1.90" H 4650 1300 50  0001 C CNN "ALV0%€"
	1    4650 1300
	1    0    0    -1  
$EndComp
$EndSCHEMATC
