<template>
  <v-snackbar
    :value="Object.keys(status).filter((k) => {return status[k] != Status.SUCCESS}).length"
    color="error"
    :timeout="0"
    top right
    @click="show = !show"
  >
    <v-tooltip v-if="server_connected != Status.SUCCESS" bottom v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-server-off</v-icon>
      </template>
      {{t('StatusBar/Lainuri_server_connection_lost')}}
    </v-tooltip>
    <v-tooltip v-if="status.thermal_printer_status != Status.SUCCESS" left v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-printer-off</v-icon>
      </template>
      {{t('StatusBar/Printer_off')}}
    </v-tooltip>
    <v-tooltip v-if="status.thermal_printer_paper_status == Status.ERROR" bottom v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-paper-roll</v-icon>
      </template>
      {{t('StatusBar/Printer_paper_runout')}}
    </v-tooltip>
    <v-tooltip v-if="status.thermal_printer_paper_status != Status.SUCCESS" left v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon color="yellow darken-2" v-on="on">mdi-paper-roll-outline</v-icon>
      </template>
      {{t('StatusBar/Printer_paper_low')}}
    </v-tooltip>
    <v-tooltip v-if="status.rfid_reader_status != Status.SUCCESS" left v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-access-point</v-icon>
      </template>
      {{t('StatusBar/RFID_reader_off')}}
    </v-tooltip>
    <v-tooltip v-if="status.barcode_reader_status != Status.SUCCESS" bottom v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-barcode</v-icon>
      </template>
      {{t('StatusBar/Barcode_reader_off')}}
    </v-tooltip>
    <v-tooltip v-if="status.ils_connection_status != Status.SUCCESS" left v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-if="status.ils_connection_status == Status.ERROR"   color="error" v-on="on">mdi-server-network-off</v-icon>
        <v-icon v-if="status.ils_connection_status == Status.PENDING" color="yellow darken-2" v-on="on">mdi-server-network-off</v-icon>
      </template>
      {{t('StatusBar/ILS_connection_lost')}}
    </v-tooltip>
  </v-snackbar>
</template>

<script>
import {Status} from '../lainuri_events.js'

export default {
  name: 'StatusBar',
  created: () => {
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
      this.$data.status = event
    });
  },
  data: () => ({
    // Include imports
    Status: Status,

    server_connected: Status.ERROR,
    status: {
      barcode_reader_status = Status.ERROR,
      thermal_printer_status = Status.ERROR,
      thermal_printer_paper_status = Status.ERROR,
      rfid_reader_status = Status.ERROR,
      touch_screen_status = Status.ERROR,
      ils_connection_status = Status.ERROR,
    },

    show: false,
  }),
}
</script>

<style scoped>

</style>
