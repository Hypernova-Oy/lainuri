<template>
    <v-card
      ripple
      raised
      v-bind:class="{
        error: note.status === 'failed' || note.status === 'error',
      }"
      @click="$emit('close_notification')"
    >
      <span class="content">
        <v-card-title v-text="note.title || '...'"></v-card-title>
      </span>
        <ItemCard :item_bib="note.item_bib"/>
      <v-img
        v-if="note.image"
        :src="note.image"
        contain
        height="100%"
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
    note: Object,
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
