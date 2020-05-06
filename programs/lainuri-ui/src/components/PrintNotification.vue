<template>
  <v-overlay :value="receipt_printing">
    <v-container centered>
    <v-card
      ripple
      raised
      @click="$emit('close_notification')"
    >
      <h1>{{t('PrintNotification/Take_the_receipt')}}</h1>
    </v-card>
    <ArrowSliding/>
    </v-container>
  </v-overlay>
</template>

<script>
import ArrowSliding from '../components/ArrowSliding.vue'

export default {
  name: 'PrintNotification',
  components: {
    ArrowSliding,
  },
  props: {
    receipt_printing: Boolean,
  },
  data: () => ({}),
  created: function () {},
}
</script>

<style scoped>
h1 {
  padding: 100px;
}
#arrowAnim {
    margin-top: -50vw;
}
</style>
