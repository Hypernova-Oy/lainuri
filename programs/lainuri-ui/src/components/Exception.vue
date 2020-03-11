<template>
  <v-alert
    prominent
    type="error"
    v-on:click.native="close"
  >
    <v-row align="center">
      <v-col class="grow">{{exceptions_count > 1 ? '('+exceptions_count+')' : ''}} {{t('Exception/'+e_type)}}</v-col>
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
    exceptions_count: Number,
  },
  updated: function () {
    this.start_close_timeout()
  },
  computed: {
    // Normalize invocations, detect if Exception object is given, or a event, or a ItemBib
    e_type: function () {
      this.start_close_timeout()
      if (this.exception.status && this.exception.states && this.exception.states.exception && this.exception.states.exception.type) return this.exception.states.exception.type;
      if (this.exception.type) return this.exception.type;
      return '<NO EXCEPTION TYPE>'
    },
    e_trace: function () {
      if (this.exception.status && this.exception.states && this.exception.states.exception && this.exception.states.exception.trace) return this.exception.states.exception.trace;
      if (this.exception.trace) return this.exception.trace;
      return '<NO EXCEPTION TRACE>'
    }
  },
  methods: {
    start_close_timeout: function () {
      if (this.close_timeout) window.clearTimeout(this.close_timeout);
      this.close_timeout = window.setTimeout(
        function() {this.close()}.bind(this),
        5000
      );
    },
    close: function () {
      this.$emit('exception_close')
    },
  },
}
</script>

<style scoped>

</style>
