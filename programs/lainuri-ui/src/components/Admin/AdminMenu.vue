<template>
  <v-card class="admin-menu">
    <v-tabs v-model="view">
      <v-tab>
        <v-icon>mdi-paper-roll</v-icon>Template Editor
      </v-tab>
      <v-tab>
        <v-icon>mdi-cog</v-icon>Config Editor
      </v-tab>
      <v-tab @click="close_admin_menu">
        <v-icon>mdi-close-circle</v-icon>Exit
      </v-tab>
      <v-tab-item>
        <TemplateEditor
          v-if="view === 0"
          />
      </v-tab-item>
      <v-tab-item>
        <!-- Disabled due to a bug in vjfs (vuetify json-schema forms) -->
        <ConfigEditor
          v-if="view === 9999"
          />
      </v-tab-item>
    </v-tabs>
  </v-card>
</template>

<script>
import {lainuri_ws} from '../../lainuri'
import {LEUserLoginComplete, LEUserLoggingIn, LEUserLoginAbort} from '../../lainuri_events'

import ConfigEditor from '../../components/Admin/ConfigEditor.vue'
import TemplateEditor from '../../components/Admin/TemplateEditor.vue'

export default {
  name: 'AdminMenu',
  components: {
    ConfigEditor,
    TemplateEditor,
  },
  data: () => ({
    view: '',
  }),
  created: function () {

  },
  methods: {
    close_template_editor: function () {

    },
    close_admin_menu: function () {
      this.$emit('close_admin_menu')
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
