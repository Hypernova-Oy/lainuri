<template>
  <v-alert
    prominent
    type="error"
    v-on:click.native="$emit('exception_close')"
  >
    <v-row align="center">
      <v-col class="grow">{{except_str}}</v-col>
      <v-col class="shrink">
        <v-btn>OK</v-btn>
      </v-col>
    </v-row>
  </v-alert>
</template>

<script>
export default {
  name: 'Exception',
  props: {
    except_str: String,
  },
}
</script>

<style scoped>

</style>
