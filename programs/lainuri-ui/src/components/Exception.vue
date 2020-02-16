<template>
  <v-alert
    prominent
    type="error"
    v-on:click.native="$emit('exception_close')"
  >
    <v-row align="center">
      <v-col class="grow">{{exception}}</v-col>
      <v-col class="shrink">
        <v-btn x-large>OK</v-btn>
      </v-col>
    </v-row>
  </v-alert>
</template>

<script>
export default {
  name: 'Exception',
  props: {
    exception: Object,
  },
}
</script>

<style scoped>

</style>
