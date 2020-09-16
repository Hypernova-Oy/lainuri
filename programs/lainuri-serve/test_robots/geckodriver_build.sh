## IN THIS FILE
##
## Compiles geckodriver for armv7l
##
## INITIAL SCRIPT
##
## https://gist.github.com/nestukh/4da25f3aa2360d770490ee434bff3dde
##
##


#!/bin/bash

pypcks="python3-pip python3 python3-all-dev python3-dev libffi-dev libssl-dev librtmp-dev python-dev python3 python3-doc python3-tk python3-setuptools tix xvfb python-bluez python-gobject python-dbus python cython python-doc python-tk python-numpy python-scipy python-qt4 python3-pyqt5 python3-pyqt5.q* python3-qtpy python-pyqt5.q* python-lxml fontconfig python-demjson qt5-default libqt5webkit5-dev build-essential libudev-dev python-lxml libxml2-dev libxslt-dev libpq-dev python-pyside python-distlib python-pip python-setuptools" # python-examples python3-examples python-vte
allgoodpcks="ca-certificates virtualenv autotools-dev cdbs git libnss3-tools util-linux xvfb curl bridge-utils chromium-browser chromium-chromedriver firefox-esrt"
sudo apt-get install --reinstall -y $pypcks $allgoodpcks

if [[ ! -f /usr/lib/chromium-browser/chromedriver ]]; then
  sudo ln -s /usr/bin/chromedriver /usr/lib/chromium-browser/chromedriver
fi

sudo pip install --upgrade pip


# python 2to3 transitional setup
sudo apt-mark hold python-pip
sudo rm -frR ~/.cache/pip
sudo rm -frR /root/.cache/pip
if [[ -f /usr/bin/pip3 ]]; then
  sudo update-alternatives --install /usr/bin/pip pip "/usr/bin/pip3" 900
else
  sudo pip3 install --upgrade pip ## prereformat
  sudo ln -s /usr/local/bin/pip3 /usr/bin/pip3
  sudo update-alternatives --install /usr/bin/pip pip "/usr/bin/pip3" 900
fi
sudo pip install --upgrade pip


python3 -m virtualenv $HOME/personal_python_env --python=$(ls -1 /usr/bin/python3* | grep -P "\d$" | tail -n1)
source $HOME/personal_python_env/bin/activate
pip install --upgrade pip
pip install --no-cache-dir requests lxml beautifulsoup4 ftfy blink1 python-librtmp pyOpenSSL pathlib certifi python-crontab pexpect python-magic pyquery regex xvfbwrapper selenium pyvirtualdisplay python-librtmp xvfbwrapper youtube_dl selenium pyvirtualdisplay


export DISPLAY=:1
sudo touch /root/.Xauthority
XAUTHORITY='/root/.Xauthority' sudo Xvfb :1 -screen 0 1280x960x16 &
sudo apt-get install --reinstall -y python3-xlib python-xlib scrot python3-tk python3-dev python-tk python-dev
pip install --no-cache-dir Xlib
pip install --no-cache-dir Pillow RPi.GPIO spidev pyautogui # pillow
sudo kill "$(ps -auxf | grep -P "sudo Xvfb .1 -screen 0 1280x960x16" | grep -v grep | sed "s/\\\\_.*$//g;s/[ \t]*$//g;s/^root[ \t]*//g;s/ .*$//g")"
unset DISPLAY
ln -s "/usr/lib/python3/dist-packages/PyQt5"  "$HOME/personal_python_env/lib/python3."*"/site-packages/"
#ln -s "/usr/lib/python2.7/dist-packages/PyQt5"  "$HOME/personal_python_env/lib/python2.7/site-packages/"
for FILE in "/usr/lib/python3/dist-packages/sip"*; do ln -s "$FILE" "$HOME/personal_python_env/lib/python3."*"/site-packages/"; done
deactivate


## https://firefox-source-docs.mozilla.org/testing/geckodriver/ARM.html
sudo apt install -y gcc-arm-linux-gnueabihf libc6-armhf-cross libc6-dev-armhf-cross
git clone --depth=1 https://github.com/mozilla/gecko-dev
curl https://sh.rustup.rs -sSf | bash -s -- -v -y
declare -a bindirs=("$HOME/.cargo/bin")
if [[ "$(cat $HOME/.bashrc | grep -P "^PATH=" )" == "" ]]; then
  echo -e "PATH=\$PATH\n" >> $HOME/.bashrc
fi
for binfolder in "${bindirs[@]}"
do
  if [[ "$(cat $HOME/.bashrc | grep -P "^PATH=" | grep "${binfolder}:")" == "" ]]; then
    sed -i -e "s/^PATH=\"\(.*\)\"/PATH=\"$(echo "$binfolder" | sed "s/\//\\\\\//g"):\1\"/g" $HOME/.bashrc # place with no spaces in it
    export PATH="$PATH:$binfolder"
  fi
done
source $HOME/.bashrc
rustup target install armv7-unknown-linux-gnueabihf
echo -e "[target.armv7-unknown-linux-gnueabihf]
linker = \"arm-linux-gnueabihf-gcc\"" > "$HOME/gecko-dev/testing/geckodriver/.cargo/config"
cd "$HOME/gecko-dev/testing/geckodriver"
cargo build --release --target armv7-unknown-linux-gnueabihf
# test binary file with this command
$HOME/gecko-dev/target/armv7-unknown-linux-gnueabihf/release/geckodriver --version


exit 0



###### open python with
source $HOME/personal_python_env/bin/activate
xvfb-run -a python -u -B ## xvfb for headless firefox-esr


####################################################
##########################
#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import io
import getpass
import six
import requests
import ssl
import certifi
import ftfy
import locale
import datetime

import platform
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from pyvirtualdisplay import Display


// start browser..
print("waiting Selenium + Firefox to load..")
display = Display(visible=0, size=(800, 600))
display.start()
mime_types = "application/gpx+tcx,application/octet-stream,application/x-pdf,application/acrobat,applications/vnd.pdf,application/pdf,text/pdf,text/x-pdf,application/vnd.cups-pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"
fp = webdriver.FirefoxProfile()
geckopath='/home/'+getpass.getuser()+'/gecko-dev/target/armv7-unknown-linux-gnueabihf/release/geckodriver'
tempdownloaddir='/home/'+getpass.getuser()+'/download'
fp.set_preference("webdriver.gecko.driver", geckopath)
fp.set_preference("browser.cache.disk.enable", False)
#fp.set_preference("browser.cache.memory.enable", False)
fp.set_preference("browser.cache.offline.enable", False)
fp.set_preference("network.http.use-cache", False)
fp.set_preference("plugin.scan.Acrobat", "99.0") #
fp.set_preference("plugin.scan.plid.all", False) #
fp.set_preference("browser.helperApps.alwaysAsk.force", False) #
fp.set_preference("browser.download.folderList", 2)
fp.set_preference("browser.download.manager.showWhenStarting", False)
fp.set_preference("browser.download.dir", tempdownloaddir)
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_types)
fp.set_preference("browser.download.manager.alertOnEXEOpen",False)
fp.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
fp.set_preference("pdfjs.disabled", True)
fp.set_preference('browser.download.manager.showAlertOnComplete', False)
fp.set_preference('browser.download.useDownloadDir', True)
fp.set_preference('browser.download.defaultFolder', tempdownloaddir)
fp.set_preference('browser.download.lastDir', tempdownloaddir)
#fp.set_preference('plugin.state.java', 2)
fp.accept_untrusted_certs = True
#fp.set_preference("security.default_personal_cert", "Select Automatically")
fp.set_preference("datareporting.healthreport.uploadEnabled", False)
#fp.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0")
fp.set_preference("general.useragent.override", "Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53")
fp.set_preference("javascript.enabled", True)
fp.set_preference("configplugins.click_to_play", True)
fp.set_preference("http.response.timeout", 9999)
fp.set_preference("dom.max_script_run_time", 9999)
fp.set_preference("permissions.default.image", 2) ## Disable images
# fp.set_preference('permissions.default.stylesheet', 2) ## Disable CSS
#fp.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',flashplugin)
fp.set_preference("media.volume_scale", "0.0")
fp.set_preference("app.update.auto", False);
fp.set_preference("app.update.lastUpdateTime.addon-background-update-timer", 1280826385);
fp.set_preference("app.update.lastUpdateTime.background-update-timer", 1280826385);
fp.set_preference("app.update.lastUpdateTime.blocklist-background-update-timer", 1280826385);
fp.set_preference("app.update.lastUpdateTime.microsummary-generator-update-timer", 1280502030);
fp.set_preference("app.update.lastUpdateTime.places-maintenance-timer", 1280826385);
fp.set_preference("app.update.lastUpdateTime.search-engine-update-timer", 1280826385);
fp.set_preference("browser.EULA.3.accepted", True);
fp.set_preference("browser.EULA.override", True);
fp.set_preference("browser.allowpopups", False);
fp.set_preference("browser.bookmarks.restore_default_bookmarks", False);
fp.set_preference("browser.history_expire_days.mirror", 180);
#fp.set_preference("browser.link.open_external", 2);
#fp.set_preference("browser.migration.version", 1);
#fp.set_preference("browser.places.smartBookmarksVersion", 1);
#fp.set_preference("browser.preferences.advanced.selectedTabIndex", 2);
#fp.set_preference("browser.privatebrowsing.autostart", True);
#fp.set_preference("browser.rights.3.shown", True);
#fp.set_preference("browser.safebrowsing.enabled", False);
fp.set_preference("browser.search.update", False);
#fp.set_preference("browser.sessionstore.resume_session_once", True);
fp.set_preference("browser.startup.homepage", "about:blank");
fp.set_preference("browser.startup.homepage_override.mstone", "rv:1.9.1.11");
fp.set_preference("browser.startup.page", 0);
fp.set_preference("browser.tabs.warnOnClose", False);
fp.set_preference("browser.tabs.warnOnOpen", False);
fp.set_preference("browser.urlbar.autocomplete.enabled", False);
fp.set_preference("dom.disable_open_during_load", False);
fp.set_preference("dom.max_chrome_script_run_time", 1800);
fp.set_preference("dom.max_script_run_time", 1800);
#fp.set_preference("extensions.lastAppVersion", "3.5.11");
fp.set_preference("extensions.update.enabled", False);
fp.set_preference("extensions.update.notifyUser", False);
fp.set_preference("idle.lastDailyNotification", 1280826384);
fp.set_preference("intl.charsetmenu.browser.cache", "UTF-8, ISO-8859-1");
fp.set_preference("network.cookie.prefsMigrated", True);
fp.set_preference("network.dns.disableIPv6", True);
fp.set_preference("network.http.phishy-userpass-length", 255);
#fp.set_preference("pref.browser.homepage.disable_button.bookmark_page", False);
#fp.set_preference("pref.browser.homepage.disable_button.current_page", False);
#fp.set_preference("pref.browser.homepage.disable_button.restore_default", False);
#fp.set_preference("privacy.sanitize.migrateFx3Prefs", True);
#fp.set_preference("privacy.sanitize.timeSpan", 0);
fp.set_preference("security.warn_entering_weak", False);
fp.set_preference("security.warn_entering_weak.show_once", False);
fp.set_preference("security.warn_viewing_mixed", False);
fp.set_preference("security.warn_viewing_mixed.show_once", False);
fp.set_preference("signon.rememberSignons", False);
#fp.set_preference("spellchecker.dictionary", "en_US");
fp.set_preference("startup.homepage_welcome_url", "");
#fp.set_preference("urlclassifier.keyupdatetime.https://sb-ssl.google.com/safebrowsing/newkey", 1287053252);
#fp.set_preference("xpinstall.whitelist.required", False);
capabilities = webdriver.DesiredCapabilities().FIREFOX
capabilities["marionette"] = True
ffoptions = Options()
#options.add_argument("--headless")
#options.add_argument("start-maximized")
#options.add_argument("--disable-gpu")
#options.add_argument("--disable-extensions")
ffbinaryx='/usr/bin/firefox-esr'
print('using Firefox in path '+ffbinaryx)
driver = webdriver.Firefox(firefox_binary=FirefoxBinary(ffbinaryx),firefox_profile=fp,options=ffoptions,executable_path=geckopath,service_log_path=os.devnull,timeout=720,capabilities=capabilities)
firefoxpid = driver.service.process.pid
print("Firefox PID = "+str(firefoxpid)+"\n")
driver.maximize_window()


// do stuff
driver.get('https://google.com') # goes to google.com
datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S');driver.save_screenshot('/home/'+getpass.getuser()+datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')+'.png') # screenshot
soup = BeautifulSoup(driver.page_source.encode('utf-8'), 'html.parser') # pass stuff to BeautifulSoup
driver.find_element_by_xpath("//div[contains(@class,'flux capacitor')]/.//li/span[contains(.,"+os.RTLD_LAZY+")]").find_element_by_xpath("..").click() # clicks somewhere
dir(driver) # lists commands and values


// quit everything
driver.quit()
displaypid=display.pid
display.stop()
// for good measure (it depends on the firefox version)
os.kill(firefoxpid, signal.SIGKILL)
os.kill(displaypid, signal.SIGKILL)
exit()
##########################
####################################################



####################
##########
// start browser..
print("waiting Selenium + Chromium to load..")
options = webdriver.ChromeOptions()
#options.binary_location='/usr/bin/chromium-browser'
#options.add_argument("--incognito")
options.add_argument("user-data-dir="+'/home/'+getpass.getuser()+'/chromiumprofiledir')
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
#options.add_argument("download.default_directory=/home/"+getpass.getuser()+"/chromiumdownloaddir")
prefs = {
    "download.default_directory" : "/home/"+getpass.getuser()+"/chromiumdownloaddir",
    "download.directory_upgrade": True,
    "download.prom  pt_for_download": False,
    "disable-popup-blocking": True,
    "safebrowsing.enabled": False,
    "safebrowsing.disable_download_protection": True,
}
options.add_experimental_option("prefs", prefs)
chromedriverpath="/usr/lib/chromium-browser/chromedriver"
driver = webdriver.Chrome(executable_path=chromedriverpath, chrome_options=options)
driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': chromiumdownloaddir}}
driver.execute("send_command", params)


// do stuff...
##########
####################




### close python env with
deactivate