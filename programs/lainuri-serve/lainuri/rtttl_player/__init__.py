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

// // // //
// LOGGER
// // // //

#define FATAL 0
#define ERROR 1
#define WARN  2
#define INFO  3
#define DEBUG 4
#define TRACE 5

short logLevel;

void loginit(short level) {
  logLevel = level;
}

void logp(const short level, char* message) {
  if (level > logLevel) {
    return;
  }

  char *tag;
  switch (level) {
    case FATAL: tag = "FATAL"; break;
    case ERROR: tag = "ERROR"; break;
    case WARN:  tag = "WARN "; break;
    case INFO:  tag = "INFO "; break;
    case DEBUG: tag = "DEBUG"; break;
    case TRACE: tag = "TRACE"; break;
  }

  printf("[%s]: %s\n", tag, message);
}
// // // //
// END OF LOGGER
// // // //



// // // //
// RTTTL PARSER
// // // //

struct Tone {
  uint32_t frequency;
  uint16_t duration;
};

struct Song {
  char name[11];
  int tonesCount;
  struct Tone tones[1024];
};

#define isdigit(n) (n >= '0' && n <= '9')

char str[121];

const uint16_t note_frequencies[9][12] =
{// C     C#    D     D#    E     F     F#    G     G#    A     A#    B     octave
  {0,    0,    0,    0,    0,    0,    0,    0,    0,    27,   29,   31  }, //0th
  {33,   35,   37,   39,   41,   44,   46,   49,   52,   55,   58,   62  }, //1st
  {65,   69,   73,   78,   82,   87,   92,   98,   104,  110,  117,  123 }, //2nd
  {131,  139,  147,  156,  165,  175,  185,  196,  208,  220,  233,  245 }, //3rd
  {262,  277,  294,  311,  330,  349,  370,  392,  415,  440,  466,  494 }, //4th
  {523,  554,  587,  622,  659,  698,  740,  784,  830,  880,  932,  988 }, //5th
  {1047, 1109, 1175, 1244, 1319, 1397, 1480, 1568, 1660, 1760, 1865, 1976}, //6th
  {2093, 2218, 2349, 2489, 2637, 2794, 2960, 3136, 3320, 3520, 3728, 3951}, //7th
  {4186, 0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0   }  //8th
};
const char *note_as_text[9][12] =
{
  {"C0", "C0#", "D0", "D0#", "E0", "F0", "F0#", "G0", "G0#", "A0", "A0#", "B0"}, //0th
  {"C1", "C1#", "D1", "D1#", "E1", "F1", "F1#", "G1", "G1#", "A1", "A1#", "B1"}, //1st
  {"C2", "C2#", "D2", "D2#", "E2", "F2", "F2#", "G2", "G2#", "A2", "A2#", "B2"}, //2nd
  {"C3", "C3#", "D3", "D3#", "E3", "F3", "F3#", "G3", "G3#", "A3", "A3#", "B3"}, //3rd
  {"C4", "C4#", "D4", "D4#", "E4", "F4", "F4#", "G4", "G4#", "A4", "A4#", "B4"}, //4th
  {"C5", "C5#", "D5", "D5#", "E5", "F5", "F5#", "G5", "G5#", "A5", "A5#", "B5"}, //5th
  {"C6", "C6#", "D6", "D6#", "E6", "F6", "F6#", "G6", "G6#", "A6", "A6#", "B6"}, //6th
  {"C7", "C7#", "D7", "D7#", "E7", "F7", "F7#", "G7", "G7#", "A7", "A7#", "B7"}  //7th
};

struct Song parse_rtttl(char *rtttl_song) {
  snprintf(str, 121, "Song parsed from rtttl '%s'", rtttl_song); logp(DEBUG, str);

  struct Song song;

  //Set defaults
  uint16_t tempo = 63;
  char duration = 4;
  char octave = 6;


  //Estimate how long the song is, to preserve enough space for the precalculated frequency array
  int i = 0;
  char *needle = rtttl_song;
  while (*needle != '\0') {
    i++;
    needle++;
  }
  i = i/2; // Half of the size of the rtttl song should suffice to fit all tones
  snprintf(str, 121, "Song is ~%d notes long", i); logp(DEBUG, str);

  //
  // Read the song name,
  //
  // character by character until the first ':'
  // The name section (JingleBell).
  // A string of characters represents the name of the melody.
  // This can be no longer than 10 characters, and cannot contain a ":" character.
  //
  i = 0;
  while (*rtttl_song != ':') {
    song.name[i++] = *rtttl_song;
    rtttl_song++;
  }
  song.name[i] = '\0';
  snprintf(str, 121, "Song is called '%s'", song.name); logp(DEBUG, str);
  rtttl_song++; // Skip over the first ':'


  //
  // Read the default value section
  //
  // The default value section (d=8,o=5,b=112)
  // Is a set of values separated by commas, where each value contains a key and a value separated by an = character,
  // which describes the melody defaults.
  // For example: d=8,o=5,b=112
  //
  while ( *rtttl_song != ':' )
  {
    if (*rtttl_song == 'd')
    {
      duration = 0;
      rtttl_song++;
      while (*rtttl_song == '=') rtttl_song++;
      while (*rtttl_song == ' ') rtttl_song++;

      // Get first digit
      if (isdigit(*rtttl_song)) duration = *rtttl_song - '0';
      rtttl_song++;

      // Get second digit
      if (isdigit(*rtttl_song)) {
        duration = duration*10 + (*rtttl_song - '0');
        rtttl_song++;
      }

      snprintf(str, 121, "Song default duration is '%d'", duration); logp(DEBUG, str);
      while (*rtttl_song == ',') rtttl_song++;
    }

    if (*rtttl_song == 'o') {
      octave = 0;
      rtttl_song++;
      while (*rtttl_song == '=') rtttl_song++;
      while (*rtttl_song == ' ') rtttl_song++;

      if (isdigit(*rtttl_song)) octave = *rtttl_song - '0';
      rtttl_song++;

      snprintf(str, 121, "Song default octave is '%d'", octave); logp(DEBUG, str);
      while (*rtttl_song == ',') rtttl_song++;
    }

    if (*rtttl_song == 'b') {
      tempo = 0;
      rtttl_song++;
      while (*rtttl_song == '=') rtttl_song++;
      while (*rtttl_song == ' ') rtttl_song++;

      // Get first digit
      if (isdigit(*rtttl_song)) tempo = *rtttl_song - '0';
      rtttl_song++;

      // Get second digit
      if (isdigit(*rtttl_song)) {
        tempo = tempo*10 + (*rtttl_song - '0');
        rtttl_song++;

        // Get third digit
        if (isdigit(*rtttl_song)) {
          tempo = tempo*10 + (*rtttl_song - '0');
          rtttl_song++;
        }
      }
      while (*rtttl_song == ',') rtttl_song++;
    }

    snprintf(str, 121, "Song default tempo is '%d'", tempo); logp(DEBUG, str);
    while (*rtttl_song == ',') rtttl_song++;
  }
  rtttl_song++; // Skip over the second ':'


  //
  // The data section (32p,a,a,4a,...,a,4g,4c6)
  //
  // Is a set of string pairs separated by commas, where each string pair contains:
  // a duration-pitch-octave and optional dotting (which increases the duration of the note by one half).
  //
  // For example:
  // 32p,8g.,16e,c,e,g,2c6,8e6,16d6,c6,e,f#,2g,g,e6,8d6,c6,2b,8a.,16b,c6,c6,g,e,c
  //

  uint8_t temp_duration, temp_octave, current_note, dot_flag, sharp_flag;
  i = 0;
  while ( *rtttl_song ) {
    struct Tone t;

    current_note = 255;
    temp_octave = octave;
    temp_duration = duration;
    dot_flag = 0;
    sharp_flag = 0;

    // Parse digit
    if ( *rtttl_song >= '0' && *rtttl_song <= '9' ) {
      temp_duration = *rtttl_song - '0';
      rtttl_song++;
      if ( *rtttl_song >= '0' && *rtttl_song <= '9' ) {
        temp_duration = temp_duration*10 + (*rtttl_song - '0');
        rtttl_song++;
      }
    }

    switch (*rtttl_song) {
      case 'c': current_note = 0;   break;
      case 'd': current_note = 2;   break;
      case 'e': current_note = 4;   break;
      case 'f': current_note = 5;   break;
      case 'g': current_note = 7;   break;
      case 'a': current_note = 9;   break;
      case 'b': current_note = 11;  break;
      case 'p': current_note = 255; break;
    }
    rtttl_song++;

    if (*rtttl_song=='#') {
      current_note++;
      sharp_flag = 1;

      rtttl_song++;
    }

    if (*rtttl_song=='.') {
      dot_flag = 1;
      rtttl_song++;
    }

    if (*rtttl_song >= '0' && *rtttl_song <= '9') {
      temp_octave = *rtttl_song - '0';
      rtttl_song++;
    }

    if (*rtttl_song=='.'){
      dot_flag = 1;
      rtttl_song++;
    }

    while (*rtttl_song == ',') rtttl_song++;




    t.duration = ( 60000/tempo ) / ( temp_duration );
    t.duration *= 4;
    if (dot_flag) {
      t.duration = t.duration * 1.5;
    }

    const char *note;
    if ( current_note < 255 ) {
      t.frequency = note_frequencies[temp_octave][current_note];
      note = note_as_text[temp_octave][current_note];
    }
    else {
      t.frequency = 0;
      note = "-";
    }

    snprintf(str, 121, "Tone[%-4d]: duration %-5d, frequency %-4d, note %-3s, duration 1/%d, sharp %-1d, dot %-1d",
                       i, t.duration, t.frequency, note, temp_duration, sharp_flag, dot_flag);
    logp(DEBUG, str);
    song.tones[i++] = t;
  }
  song.tonesCount = i;

  return song;
}
// // // //
// END OF RTTTL PARSER
// // // //


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
