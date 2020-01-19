<template>
    <v-card
      ripple
      raised
      max-width="250px"
      v-bind:class="[item_bib.checkout_status]"
      class=""
      @click="overlay = !overlay"
    >
      <v-img
        :src="item_bib.book_cover_url"
        contain
        class="white--text align-end"
        gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"

      >
        <v-progress-circular
          v-if="item_bib.checkout_status === 'pending'"
          class="progress"
          size="150"
          width="25"
          color="primary"
          indeterminate
        ></v-progress-circular>
      </v-img>
      <v-card-title v-text="item_bib.title || '...'"></v-card-title>
      <v-card-subtitle><div>{{item_bib.author || 'x'}}</div><div>{{item_bib.edition || 'x'}}</div></v-card-subtitle>
      <v-card-text v-text="item_bib.item_barcode"></v-card-text>

      <v-overlay absolute :value="overlay"
        v-if="item_bib.exception"
      >
        <v-card-text>
          {{item_bib.exception}}
        </v-card-text>
      </v-overlay>
    </v-card>
</template>

<script>

export default {
  name: 'CheckOut',
  props: {
    item_bib: Object,
  },
  data: () => ({
    overlay: false,
  }),
}
</script>

<style scoped>
.progress {
  position: absolute;
  top: 25%;
  left: 20%;
}

</style>
