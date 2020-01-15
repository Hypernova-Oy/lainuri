<template>
  <v-col>
    <v-card ripple raised width="250px">
      <v-img
        :src="item_bib.book_cover_url"
        contain
        class="white--text align-end"
        gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
        height="300px"
      >
      </v-img>
      <v-card-title v-text="item_bib.title || '...'"></v-card-title>
      <v-card-subtitle><div>{{item_bib.author || 'x'}}</div><div>{{item_bib.edition || 'x'}}</div></v-card-subtitle>
      <v-card-text v-text="item_bib.barcode"></v-card-text>
    </v-card>
  </v-col>
</template>

<script>

export default {
  name: 'CheckOut',
  props: {
    item_bib: Object,
  },
}
</script>

<style scoped>

</style>
