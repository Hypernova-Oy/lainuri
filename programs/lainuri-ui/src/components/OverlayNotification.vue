<template>
<span>
    <v-progress-linear striped reverse height="10"
      v-model="timeout_left"
      :color="(item_bib.status === Status.SUCCESS && 'success') || 'error'"/>
  <v-card
    raised
    :ripple="false"
    v-bind:class="{
      error: item_bib.status === Status.ERROR,
      overlay_notification: true,
    }"
    @click="close_notification"
  >
    <v-icon class="close-overlay-icon">mdi-close-box</v-icon>
    <h1 v-if="     mode === 'checkin'">{{t('CheckIn/'+notification_type)}}</h1>
    <h1 v-else-if="mode === 'checkout' && notification_type === 'Place_to_RFID_reader'">{{t('CheckOut/'+notification_type)}}</h1>
    <h1 v-else-if="mode === 'checkout' && item_bib.status == Status.ERROR">{{t('CheckOut/Check_out_failed')}}</h1>
    <h1 v-else-if="mode === 'checkout' && item_bib.status == Status.SUCCESS">{{t('CheckOut/Be_advised!')}}</h1>
    <ItemCard :item_bib="item_bib" :ripple_show="true"/>
    <v-img
      v-if="mode === 'checkin' || (mode === 'checkout' && notification_type === 'Place_to_RFID_reader')"
      :src="notification_type && $appConfigGetImageOverload(notification_type)"
      contain
      class="white--text align-end"
      gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
    />
  </v-card>
</span>
</template>

<script>
import {get_logger} from '../logger'
let log = get_logger('OverlayNotification.vue');

import {Status} from '../lainuri_events.js'
import ItemCard from '../components/ItemCard.vue'
import * as Timeout from '../timeout_poller'

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
    timeout_left: 100,
  }),
  created: function () {
    if (this.$appConfig.ui.popup_inactivity_timeout_s) {
      Timeout.start('OverlayNotificationTimeout',
        undefined,
        undefined,
        () => {
          this.$data.timeout_left -= 100 / this.$appConfig.ui.popup_inactivity_timeout_s;
          if (this.$data.timeout_left < -5) this.close_notification();
        },
        1000
      );
    }
  },
  destroyed: function () {
    if (this.$appConfig.ui.popup_inactivity_timeout_s) Timeout.terminate('OverlayNotificationTimeout');
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
        if ((states_keys.length == 1 && this.item_bib.states['State/not_checked_out']) || // TODO refactor this silly decision tree.
            (states_keys.length == 1 && this.item_bib.states['State/outstanding_fines']) ||
            (states_keys.length == 2 && this.item_bib.states['State/outstanding_fines']
                                     && this.item_bib.states['State/not_checked_out']))
          return 'Place_to_bin_OK';
        else return 'Place_to_bin_ODD';
      }
      return 'Place_to_bin_OK';
    },
  },
  methods: {
    close_notification: function () {
      log.info('close_notification():> item_bib=', this.item_bib.item_barcode);
      if (this.$appConfig.ui.popup_inactivity_timeout_s) Timeout.terminate('OverlayNotificationTimeout');
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
.overlay_notification .close-overlay-icon {
  position: absolute;
  right: 0px;
  top: 0px;
}
</style>
