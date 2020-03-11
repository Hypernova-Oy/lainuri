<template>
  <v-card
    ripple
    raised
    v-bind:class="{
      error: item_bib.status === Status.ERROR,
    }"
    @click="$emit('close_notification')"
    style="padding: 20px;"
  >
    <h1 v-if="mode === 'checkin'">{{t('CheckIn/Place_to_bin_1')}}</h1>
    <h1 v-if="mode === 'checkout'">{{t('CheckOut/Check_out_failed')}}</h1>
    <ItemCard :item_bib="item_bib"/>
    <v-img
      v-if="mode === 'checkin'"
      src="place_to_bin_right.png"
      contain
      class="white--text align-end"
      gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
    />
  </v-card>
</template>

<script>
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
}
</script>

<style scoped>
.itemcard {
  margin: auto;
}
</style>
