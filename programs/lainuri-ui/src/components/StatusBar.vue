<template>
  <v-snackbar
    :value="Object.keys(status).filter((k) => {return status[k] != Status.SUCCESS}).length"
    color="error"
    :timeout="0"
    top right
    @click="show = !show"
  >
    <v-tooltip v-if="status.server_connected != Status.SUCCESS" bottom v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-server-off</v-icon>
      </template>
      {{t('StatusBar/Lainuri_server_connection_lost')}}
    </v-tooltip>
    <v-tooltip v-if="status.printer_off != Status.SUCCESS" left v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-printer-off</v-icon>
      </template>
      {{t('StatusBar/Printer_off')}}
    </v-tooltip>
    <v-tooltip v-if="status.printer_paper_out != Status.SUCCESS" bottom v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-paper-roll</v-icon>
      </template>
      {{t('StatusBar/Printer_paper_runout')}}
    </v-tooltip>
    <v-tooltip v-if="status.printer_paper_low != Status.SUCCESS" left v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-paper-roll-outline</v-icon>
      </template>
      {{t('StatusBar/Printer_paper_low')}}
    </v-tooltip>
    <v-tooltip v-if="status.printer_receipt_not_torn != Status.SUCCESS" bottom v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-receipt</v-icon>
      </template>
      {{t('StatusBar/Printer_receipt_not_torn')}}
    </v-tooltip>
    <v-tooltip v-if="status.rfid_reader_off != Status.SUCCESS" left v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-access-point</v-icon>
      </template>
      {{t('StatusBar/RFID_reader_off')}}
    </v-tooltip>
    <v-tooltip v-if="status.barcode_reader_off != Status.SUCCESS" bottom v-model="show">
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
  props: {
    status: {
      server_connected: Status,
      printer_off: Status,
      printer_paper_low: Status,
      printer_paper_out: Status,
      printer_receipt_not_torn: Status,
      rfid_reader_off: Status,
      barcode_reader_off: Status,
      ils_connection_status: Status,
    },
  },
  data: () => ({
    // Include imports
    Status: Status,

    show: false,
  }),
}
</script>

<style scoped>

</style>
