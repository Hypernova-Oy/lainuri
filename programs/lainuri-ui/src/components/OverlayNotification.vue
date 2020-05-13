<template>
  <v-card
    raised
    v-bind:class="{
      error: item_bib.status === Status.ERROR,
      overlay_notification: true,
    }"
    @click="close_notification"
  >
    <h1 v-if="     mode === 'checkin'">{{t('CheckIn/'+notification_type)}}</h1>
    <h1 v-else-if="mode === 'checkout' && notification_type === 'Place_to_RFID_reader'">{{t('CheckOut/'+notification_type)}}</h1>
    <h1 v-else-if="mode === 'checkout' && item_bib.status == Status.ERROR">{{t('CheckOut/Check_out_failed')}}</h1>
    <h1 v-else-if="mode === 'checkout' && item_bib.status == Status.SUCCESS">{{t('CheckOut/Be_advised!')}}</h1>
    <ItemCard :item_bib="item_bib"/>
    <v-img
      v-if="mode === 'checkin'"
      :src="notification_type && $appConfigGetImageOverload(notification_type)"
      contain
      class="white--text align-end"
      gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
    />
  </v-card>
</template>

<script>
import {get_logger} from '../logger'
let log = get_logger('OverlayNotification.vue');

import {Status} from '../lainuri_events.js'
import ItemCard from '../components/ItemCard.vue'

export default {
  name: 'OverlayNotification',
  components: {
    ItemCard,
  },
  props: {
    item_bib: Object,
    mode: String,
  },
  data: () => ({
    // Include imports
    Status: Status,
  }),
  created: function () {
  },
  computed: {
    /**
     * Basically does the checkin status routing to bin, for now.
     */
    notification_type: function () {
      let states_keys = Object.keys(this.item_bib.states)
      if (states_keys.length) {
        if (this.item_bib.states['Exception/RFIDCommand'] || this.item_bib.states["Exception/TagNotDetected"]) {
          return 'Place_to_RFID_reader';
        }
        if (states_keys.length == 1 && this.item_bib.states['Status/not_checked_out']) return 'Place_to_bin_OK';
        else return 'Place_to_bin_ODD';
      }
      return 'Place_to_bin_OK';
    },
  },
  methods: {
    close_notification: function () {
      log.info('close_notification():> item_bib=', this.item_bib.item_barcode);
      this.$emit('close_notification')
    }
  },
}
</script>

<style scoped>
.itemcard {
  margin: auto;
}
.overlay_notification {
  padding: 20px;
}
.overlay_notification h1 {
  margin-bottom: 20px;
}
.overlay_notification div.v-image {
  margin-top: 20px;
}
</style>
