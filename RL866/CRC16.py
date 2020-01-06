from logging_context import logging
log = logging.getLogger(__name__)

import inline
c = inline.c(r'''

#include <stdint.h>

uint16_t cal_crc16_ext(uint16_t initval, uint8_t *ptr, uint16_t len) {
  uint16_t crc;
  uint16_t i,j;
  uint8_t val;
  crc=0;
  crc= initval ;
  for(i=0;i<len;i++) {
    val =ptr[i];
    crc^=val ;
    for(j=0;j<8;j++) {
      if(crc&0x0001)
        crc=(crc>>1)^0x8408;
      else
        crc=(crc>>1);
    }
  }
  // Now the CRC-16 algorithm has produced the checksum

  // For some reason the bytes are in wrong order so switch them.
  unsigned char *p = (unsigned char*)&crc;
  unsigned char tmp = p[0];
  p[0] = p[1];
  p[1] = tmp;

  return(crc);
}

''')

def crc16(byteArray):
  return c.cal_crc16_ext(0xFFFF, byteArray, len(byteArray)).to_bytes(2, byteorder='big')
