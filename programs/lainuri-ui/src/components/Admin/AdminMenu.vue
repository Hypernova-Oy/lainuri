<template>
  <v-card class="admin-menu">
    <v-tabs v-model="view">
      <v-tab>
        <v-icon>mdi-chart-bar</v-icon>Statistics
      </v-tab>
      <v-tab>
        <v-icon>mdi-paper-roll</v-icon>Template Editor
      </v-tab>
      <v-tab>
        <v-icon>mdi-cog</v-icon>Config Editor
      </v-tab>
      <v-tab @click="enable_repl">
        <v-icon>mdi-console</v-icon>REPL
      </v-tab>
      <v-tab @click="close_admin_menu">
        <v-icon>mdi-close-circle</v-icon>Exit
      </v-tab>
    </v-tabs>
      <v-card v-if="view === 0">
        <StatisticsView
          v-on:exception="bubble_exception"
        />
      </v-card>
      <v-card v-if="view === 1">
        <TemplateEditor
          v-on:exception="bubble_exception"
        />
      </v-card>
      <v-card v-if="view === 2">
        Disabled due to a bug in vjfs (vuetify json-schema forms)
        <ConfigEditor
          v-if="view === 9999"
          v-on:exception="bubble_exception"
          />
      </v-card>
      <v-card v-if="view === 3">
        <p>REPL allows you to run code against the running GUI. This is sometimes needed to debug and develop the application. You can try writing</p>
        <p>alert("Hello World")</p>
        <p>to the REPL-panel</p>
      </v-card>
  </v-card>
</template>

<script>
import {lainuri_ws} from '../../lainuri'
import {LEUserLoginComplete, LEUserLoggingIn, LEUserLoginAbort} from '../../lainuri_events'

import ConfigEditor from '../../components/Admin/ConfigEditor.vue'
import StatisticsView from '../../components/Admin/StatisticsView.vue'
import TemplateEditor from '../../components/Admin/TemplateEditor.vue'

export default {
  name: 'AdminMenu',
  components: {
    ConfigEditor,
    StatisticsView,
    TemplateEditor,
  },
  data: () => ({
    view: '',
  }),
  created: function () {

  },
  methods: {
    bubble_exception: function (exception) {
      this.$emit('exception', exception);
    },
    close_admin_menu: function () {
      this.$emit('close_admin_menu')
    },
    enable_repl: function () {
      this.$emit('enable_repl')
    },
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.admin-menu {
  max-height: 800px;
}
</style>
