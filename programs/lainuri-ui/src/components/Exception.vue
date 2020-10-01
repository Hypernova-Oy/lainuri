<template>
  <v-alert
    prominent
    type="error"
    v-on:click.native="close"
  >
    <v-row align="center">
      <v-col class="grow">{{t('Exception/'+e_type)}} {{exception.description}}</v-col>
      <v-col class="shrink">
        <v-btn x-large>OK</v-btn>
      </v-col>
    </v-row>
  </v-alert>
</template>

<script>

import * as Timeout from '../timeout_poller'

export default {
  name: 'Exception',
  props: {
    exception: Object,
    exceptions_count: Number,
    eid: Number, // Used to uniquely identify the exception instance so we can trigger specific timers for it
  },
  created: function () {
    Timeout.start("exception"+this.eid, () => {
      this.$emit('exception_close')
    }, this.$appConfig.ui.popup_inactivity_timeout_s);
  },
  destroyed: function () {
    Timeout.terminate("exception"+this.eid)
  },
  computed: {
    // Normalize invocations, detect if Exception object is given, or a event, or a ItemBib
    e_type: function () {
      if (this.exception.status && this.exception.states && this.exception.states.exception && this.exception.states.exception.type) return this.exception.states.exception.type;
      if (this.exception.type) return this.exception.type;
      if (this.exception.etype) return this.exception.etype;
      return '<NO EXCEPTION TYPE>'
    },
    e_trace: function () {
      if (this.exception.status && this.exception.states && this.exception.states.exception && this.exception.states.exception.trace) return this.exception.states.exception.trace;
      if (this.exception.trace) return this.exception.trace;
      return '<NO EXCEPTION TRACE>'
    }
  },
  methods: {
    close: function () {
      this.$emit('exception_close')
    },
  },
}
</script>

<style scoped>
* {
  font-size: 1.2em;
}
</style>
