from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import inline
c = inline.c(r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <wiringPi.h>
#include <softTone.h>
#include "rtttl_parser.h"
#include "logger.h"

int pwmpin = 18; // Default pin, GPIO 18, only pin with hardware PWM

char str[121];

short hardware = 0; // Is hardware pwm in use? Otherwise uses the software tone library

void rtttl_graceful_terminate(int signo){
  pwmWrite(pwmpin, 0);
  pinMode(pwmpin, OUTPUT); // Disable the hardware pwm
  exit(0);
}

void init_common(short loglevel) {
  loginit(loglevel);
  wiringPiSetupGpio();
}

void init_hard() {
  hardware = 1;

  pinMode(pwmpin, PWM_OUTPUT);
  pwmSetMode(PWM_MODE_MS);
  pwmSetClock(16); // Nominal 1.2 MHz. Fix the hard-coded value 1.2e6 in code if you change this.

  // Unlike the software pwm mode, we need to manually take care to
  // handle crashes and interrupts etc, otherwise the pwm stays on
  // in the previous mode, making a lot of noise.
  struct sigaction psa;
  psa.sa_handler = rtttl_graceful_terminate;
  sigaction(SIGTSTP, &psa, NULL); // Ctrl-Z   suspend
  sigaction(SIGINT, &psa, NULL);  // Ctrl-C   interrupt
  sigaction(SIGHUP, &psa, NULL);  //          hangup - called when parent process exits
}

void init_soft() {
  hardware = 0;
  softToneCreate(pwmpin);
}

void init(int pin, short loglevel) {
  if (pin > -1) pwmpin = pin;
  init_common(loglevel);

  if (pwmpin = 18) return init_hard();
  return init_soft();
}

void play_tone(int frequency, int duration) {
  if (hardware == 1) {
    if (frequency == 0) {
      pwmWrite(pwmpin, 0); //Duty cycle is not at 0%
      delay(duration);
    }
    else {
      // This is a difficult thing:
      // https://raspberrypi.stackexchange.com/questions/53854/driving-pwm-output-frequency
      // pwmFrequency in Hz = 19.2e6 Hz / pwmClock / pwmRange
      // PWM Range = PWM frequency / Desired Output Frequency
      // PWM clock rate is set to 1.2MHz => 1.2e6
      int pwmRange = 1.2e6 / frequency;
      int pwmData = pwmRange / 2; // 50% duty cycle is loudest for a piezo

      pwmSetRange(pwmRange);
      pwmWrite(pwmpin, pwmData);
      snprintf(str, 121, "play_tone(pin=%i, freq=%-4i, dur=%-4i, pwmRange=%d)", pwmpin, frequency, duration, pwmRange); logp(DEBUG, str);
      delay(duration);
    }
  }
  else {
    snprintf(str, 121, "play_tone(pin=%i, freq=%-4i, dur=%-4i)", pwmpin, frequency, duration); logp(DEBUG, str);
    softToneWrite(pwmpin, frequency);
    delay(duration);
  //  softToneWrite(pwmpin, 0);
  }
}

void play_rtttl(char *rtttl) {
  struct Song song = parse_rtttl(rtttl);

  snprintf(str, 121, "play_rtttl(song=%s)", song.name); logp(INFO, str);

  int i = 0;
  while (i < song.tonesCount) {
    struct Tone tone = song.tones[i];
    play_tone(tone.frequency, tone.duration);
    i++;
  }
  play_tone(0, 1); // Shut down the piezo
}


//
// If compiled as a stand-alone program
// Runs a simple test suite
//
#ifndef NOMAIN

// Have a default song for testing purposes
char *song = "Axelf:d=8,o=5,b=160:4f#,a.,f#,16f#,a#,f#,e,4f#,c6.,f#,16f#,d6,c#6,a,f#,c#6,f#6,16f#,e,16e,c#,g#,4f#.";
// char *song = "nyancat:d=4,o=5,b=90:16d#6,16e6,8f#6,8b6,16d#6,16e6,16f#6,16b6,16c#7,16d#7,16c#7,16a#6,8b6,8f#6,16d#6,16e6,8f#6,8b6,16c#7,16a#6,16b6,16c#7,16e7,16d#7,16e7,16c#7,8f#6,8g#6,16d#6,16d#6,16p,16b,16d6,16c#6,16b,16p,8b,8c#6,8d6,16d6,16c#6,16b,16c#6,16d#6,16f#6,16g#6,16d#6,16f#6,16c#6,16d#6,16b,16c#6,16b,8d#6,8f#6,16g#6,16d#6,16f#6,16c#6,16d#6,16b,16d6,16d#6,16d6,16c#6,16b,16c#6,8d6,16b,16c#6,16d#6,16f#6,16c#6,16d#6,16c#6,16b,8c#6,8b,8c#6,8f#6,8g#6,16d#6,16d#6,16p,16b,16d6,16c#6,16b,16p,8b,8c#6,8d6,16d6,16c#6,16b,16c#6,16d#6,16f#6,16g#6,16d#6,16f#6,16c#6,16d#6,16b,16c#6,16b,8d#6,8f#6,16g#6,16d#6,16f#6,16c#6,16d#6,16b,16d6,16d#6,16d6,16c#6,16b,16c#6,8d6,16b,16c#6,16d#6,16f#6,16c#6,16d#6,16c#6,16b,8c#6,8b,8c#6,8b,16f#,16g#,8b,16f#,16g#,16b,16c#6,16d#6,16b,16e6,16d#6,16e6,16f#6,8b,8b,16f#,16g#,16b,16f#,16e6,16d#6,16c#6,16b,16f#,16d#,16e,16f#,8b,16f#,16g#,8b,16f#,16g#,16b,16b,16c#6,16d#6,16b,16f#,16g#,16f#,8b,16b,16a#,16b,16f#,16g#,16b,16e6,16d#6,16e6,16f#6,8b,8a#,8b,16f#,16g#,8b,16f#,16g#,16b,16c#6,16d#6,16b,16e6,16d#6,16e6,16f#6,8b,8b,16f#,16g#,16b,16f#,16e6,16d#6,16c#6,16b,16f#,16d#,16e,16f#,8b,16f#,16g#,8b,16f#,16g#,16b,16b,16c#6,16d#6,16b,16f#,16g#,16f#,8b,16b,16a#,16b,16f#,16g#,16b,16e6,16d#6,16e6,16f#6,8b,8c#6";

int main(int argc,char const *argv[])
{
  init(pwmpin, TRACE);
  play_rtttl(song);
  return 0;
}
#endif

''')

import _thread as thread
import threading

from lainuri.event import LEvent

event_play_ringtone = threading.Event()
play_ringtone_event = None

def play_rtttl(ringtone: str):
  log.info(f"Playing rtttl '{ringtone}'")
  c.play_rtttl(play_rtttl)
  log.info("Stopped playing rtttl")

def rtttl_daemon():
  while(1):
    event_play_ringtone.wait()
    event_play_ringtone.clear()
    import lainuri.rtttl_player # Initializes the RTTTL-Player on import
    if play_ringtone_event.ringtone:
      lainuri.rtttl_player.play_rtttl(lainuri.config.get_ringtone(play_ringtone_event.message.ringtone))
      lainuri.websocket_server.push_event(LEvent("ringtone-played", {'ringtone': play_ringtone_event.message.ringtone}))
    else:
      lainuri.rtttl_player.play_rtttl(lainuri.config.get_ringtone(play_ringtone_event.message.ringtone_type))
      lainuri.websocket_server.push_event(LEvent("ringtone-played", {'ringtone_type': play_ringtone_event.message.ringtone_type}))

  log.info(f"Terminating RTTTL-Player thread")
  exit(0)
thread.start_new_thread(rtttl_daemon, ())
