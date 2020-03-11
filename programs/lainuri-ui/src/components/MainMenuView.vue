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
          v-for="(item) in rfid_tags_present"
          :key="item.item_barcode"
          align="center"
          justify="center"
        >
          <ItemCard v-bind:key="item.item_barcode" :item_bib="item"/>
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
}
</script>

<style scoped>

</style>
