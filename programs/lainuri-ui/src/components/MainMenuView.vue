<template>
  <v-card
    v-if="rfid_tags_present.length"
    min-width="345"
    class="mx-auto"
  >
    <v-app-bar
      color="primary"
      dark
    >
      <v-toolbar-title>{{t('MainMenuView/RFID_tags_found')}}</v-toolbar-title>

      <v-spacer></v-spacer>

    </v-app-bar>

    <v-container class="item_scrollview">
      <v-row dense>
        <v-col
          v-for="(item_bib) in rfid_tags_present"
          :key="item_bib.item_barcode || item_bib.serial_number"
          align="center"
          justify="center"
        >
          <ItemCard v-bind:key="item_bib.item_barcode || item_bib.serial_number" :item_bib="item_bib"/>
        </v-col>
      </v-row>
    </v-container>
  </v-card>
</template>

<script>
import ItemCard from '../components/ItemCard.vue'

export default {
  name: 'MainMenuView',
  components: {
    ItemCard,
  },
  props: {
    rfid_tags_present: Array,
  },
  methods: {
  },
  data: () => ({
  }),
}
</script>

<style scoped>
.v-toolbar__title {
  font-weight: 900;
  font-size: 1.5rem;
}
</style>
