<template>
  <v-card
    ripple
    raised
    v-bind:class="{
      error: item_bib.status === 'failed' || item_bib.status === 'error',
    }"
    @click="$emit('close_notification')"
    style="padding: 20px;"
  >
    <h1 v-if="mode === 'checkin'">LAITA HYLLYYN OIKEALLA</h1>
    <h1 v-if="mode === 'checkout'">LAINAAMINEN EPÄONNISTUI</h1>
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
