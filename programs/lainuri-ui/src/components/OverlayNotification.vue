<template>
  <v-card
    ripple
    raised
    v-bind:class="{
      error: item_bib.status === 'failed' || item_bib.status === 'error',
    }"
    @click="$emit('close_notification')"
  >
    <h1>LAITA HYLLYYN OIKEALLA</h1>
    {{item_bib.item_barcode}}
    <ItemCard :item_bib="item_bib"/>
    <v-img
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
