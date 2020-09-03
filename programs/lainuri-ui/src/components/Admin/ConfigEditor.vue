<template>
  <v-card class="config-editor">
    <v-toolbar
      color="cyan"
      dark
      flat
    >
    </v-toolbar>
    CONFIG EDITOR

  <v-container>
    <p>valid={{valid}}</p>
    <v-form ref="form" v-model="valid">
      <v-jsf v-model="model" :schema="$lainuriConfigSchema" :options="options" />
    </v-form>
    <v-btn color="primary" @click="$refs.form.validate()">Validate</v-btn>
  </v-container>
  </v-card>
</template>

<script>
import {get_logger} from '../../logger'
let log = get_logger('Admin/ConfigEditor.vue');

import {lainuri_ws} from '../../lainuri'
import {Status} from '../../lainuri_events.js'

export default {
  name: 'ConfigEditor',
  created: function () {

  },
  mounted: function () {

  },
  beforeDestroy: function () {
    lainuri_ws.flush_listeners_for_component(this, this.$options.name);
  },
  data () {
    return {
      model: {},
      options: {},
      valid: null
    }
  },
  computed: {

  },
  methods: {

  }
}
</script>

<style>
.config-editor {
  z-index: 100
}
.vjsf-property .v-input--selection-controls {
  margin-top: 0;
}

.vjsf-tooltip p:last-child {
  margin-bottom: 0;
}

.vjsf-property .color-picker-trigger {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: inline-block;
  border: 2px solid #ccc;
}

.vjsf-property .color-picker-trigger-empty {
  background: linear-gradient(to top right,transparent 0,transparent calc(50% - 2.4px),#de080a 50%,transparent calc(50% + 2.4px),transparent);
}

.vjsf-date-time .v-picker.v-card {
  border-radius: 0;
}
</style>
