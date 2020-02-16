<template>
  <v-snackbar
    :value="Object.keys(status).filter((k) => {return status[k]}).length"
    color="error"
    :timeout="0"
    top right
    @click="show = !show"
  >
    <v-tooltip v-if="status.server_off" bottom v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-server-off</v-icon>
      </template>
      BÄKKÄRIVIRHE
    </v-tooltip>
    <v-tooltip v-if="status.printer_off" bottom v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-printer-off</v-icon>
      </template>
      PRINTER OFF
    </v-tooltip>
    <v-tooltip v-if="status.printer_paper_out" bottom v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-paper-roll</v-icon>
      </template>
      PAPER ROLL OUT
    </v-tooltip>
    <v-tooltip v-if="status.printer_paper_low" bottom v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-paper-roll-outline</v-icon>
      </template>
      PAPER ROLL LOW
    </v-tooltip>
    <v-tooltip v-if="status.printer_receipt_not_torn" bottom v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-receipt</v-icon>
      </template>
      RECEIPT
    </v-tooltip>
    <v-tooltip v-if="status.rfid_reader_off" bottom v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-access-point</v-icon>
      </template>
      RFID OFF
    </v-tooltip>
    <v-tooltip v-if="status.barcode_reader_off" bottom v-model="show">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">mdi-barcode</v-icon>
      </template>
      BARCODE OFF
    </v-tooltip>
  </v-snackbar>
</template>

<script>
export default {
  name: 'StatusBar',
  props: {
    status: {
      server_off: Boolean,
      printer_off: Boolean,
      printer_paper_low: Boolean,
      printer_paper_out: Boolean,
      printer_receipt_not_torn: Boolean,
      rfid_reader_off: Boolean,
      barcode_reader_off: Boolean,
    },
  },
  data: () => ({
    show: false,
  }),
}
</script>

<style scoped>

</style>
