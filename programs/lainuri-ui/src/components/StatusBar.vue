<template>
  <div
    v-show="statusbar_width"
    class="status-bar error v-snack__wrapper"
    @click="show_tooltips = !show_tooltips"
    :style="{minWidth: statusbar_width + 'px'}"
  >
  <div class="v-snack__content">
    <v-tooltip v-if="server_connected != Status.SUCCESS" bottom v-model="show_tooltips">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-server-off</v-icon>
      </template>
      {{t('StatusBar/Lainuri_server_connection_lost')}}
    </v-tooltip>
    <v-tooltip v-if="status.thermal_printer_status != Status.SUCCESS" left v-model="show_tooltips">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-printer-off</v-icon>
      </template>
      {{t('StatusBar/Printer_off')}}
    </v-tooltip>
    <v-tooltip v-if="status.thermal_printer_paper_status == Status.ERROR" bottom v-model="show_tooltips">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-paper-roll</v-icon>
      </template>
      {{t('StatusBar/Printer_paper_runout')}}
    </v-tooltip>
    <v-tooltip v-else-if="status.thermal_printer_paper_status == Status.PENDING" left v-model="show_tooltips">
      <template v-slot:activator="{ on }">
        <v-icon color="yellow darken-2" v-on="on">mdi-paper-roll-outline</v-icon>
      </template>
      {{t('StatusBar/Printer_paper_low')}}
    </v-tooltip>
    <v-tooltip v-if="status.rfid_reader_status != Status.SUCCESS" left v-model="show_tooltips">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-access-point</v-icon>
      </template>
      {{t('StatusBar/RFID_reader_off')}}
    </v-tooltip>
    <v-tooltip v-if="status.barcode_reader_status != Status.SUCCESS" bottom v-model="show_tooltips">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-barcode</v-icon>
      </template>
      {{t('StatusBar/Barcode_reader_off')}}
    </v-tooltip>
    <v-tooltip v-if="status.ils_connection_status == Status.ERROR" left v-model="show_tooltips">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-server-network-off</v-icon>
      </template>
      {{t('StatusBar/ILS_connection_lost')}}
    </v-tooltip>
    <v-tooltip v-if="status.ils_connection_status == Status.PENDING" left v-model="show_tooltips">
      <template v-slot:activator="{ on }">
        <v-icon color="yellow darken-2" v-on="on">mdi-server-network-off</v-icon>
      </template>
      {{t('StatusBar/ILS_connection_lost')}}
    </v-tooltip>
  </div>
  </div>
</template>

<script>
import {get_logger} from '../logger'
let log = get_logger('StatusBar.vue');

import {lainuri_ws} from '../lainuri'
import {Status, LEServerConnected, LEServerDisconnected, LEServerStatusResponse} from '../lainuri_events.js'

export default {
  name: 'StatusBar',
  created: function () {
    lainuri_ws.attach_event_listener(LEServerConnected, this, function(event) {
      log.info(`[StatusBar.vue]:> Event 'LEServerConnected' received.`);
      this.$data.server_connected = Status.SUCCESS;
    });
    lainuri_ws.attach_event_listener(LEServerDisconnected, this, function(event) {
      log.info(`[StatusBar.vue]:> Event 'LEServerDisconnected' received.`);
      this.$data.server_connected = Status.ERROR;
    });
    lainuri_ws.attach_event_listener(LEServerStatusResponse, this, function(event) {
      log.info(`[StatusBar.vue]:> Event 'LEServerStatusResponse' received.`);
      if (this.$data.software_version && event.statuses.software_version != this.$data.software_version) {
        log.info(`New software version detected. '${this.$data.software_version}' upgrading to '${event.statuses.software_version}'`)
        window.location.reload(true) // Force reload since a new software version was detected.
      }
      this.$data.software_version = event.statuses.software_version
      delete event.statuses.software_version
      this.$data.status = event.statuses;
    });
  },
  data: () => ({
    // Include imports
    Status: Status,

    server_connected: Status.ERROR,
    software_version: null,
    status: {
      barcode_reader_status: Status.ERROR,
      thermal_printer_status: Status.ERROR,
      thermal_printer_paper_status: Status.ERROR,
      rfid_reader_status: Status.ERROR,
      touch_screen_status: Status.ERROR,
      ils_connection_status: Status.ERROR,
    },

    show_tooltips: false,
  }),
  computed: {
    statusbar_width: function () {
      let width = 0;
      for (let key of Object.keys(this.$data.status)) {
        if (this.$data.status[key] != Status.SUCCESS) width += 32;
      }
      if (this.$data.server_connected != Status.SUCCESS) width += 32;
      return width;
    },
  },
}
</script>

<style scoped>
.status-bar {
  position: absolute;
  top: 0px;
  left: 0px;
  z-index: 99;
  margin: 3px;
}
</style>
