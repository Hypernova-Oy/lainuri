<template>
  <v-card class="template-editor">
    <v-toolbar
      color="cyan"
      dark
      flat
    >
    <v-menu bottom left>
      <template v-slot:activator="{ on }">
        <v-btn
          dark
          icon
          v-on="on"
        >
          <v-icon>mdi-menu</v-icon>
        </v-btn>
      </template>

      <v-list>
        <v-list-item
          disabled
          :key="0"
        >
          <v-toolbar-title>Receipt types</v-toolbar-title>
        </v-list-item>
        <v-list-item
          v-for="item of template_types"
          :key="item"
          @click="template_type = item"
        >
          <v-list-item-title>{{ item }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>

    <v-toolbar-title>Template editor - {{ template_type }} {{ this.$appConfig.i18n.enabled_locales[this.tab] }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <template v-slot:extension>
        <v-tabs
          v-model="tab"
          align-with-title
        >
          <v-tabs-slider color="yellow"></v-tabs-slider>
          <v-tab v-for="locale_code in $appConfig.i18n.enabled_locales" :key="template_type + locale_code">
            {{ locale_code }}
          </v-tab>
        </v-tabs>
      </template>
    </v-toolbar>

    <v-card flat>
      <v-container fluid class="grey lighten-5">
        <v-row>
          <v-col>
            <v-row>
              <v-col>
                <v-textarea
                  label="Template"
                  :error-messages="template_content_error"
                  :success="!template_content_error || true"
                  auto-grow
                  v-model="template_content"
                  @change="maybe_lazy_test_print"
                ></v-textarea>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-textarea
                  label="Template data"
                  :error-messages="template_data_validation"
                  :success="!template_data_validation || true"
                  auto-grow
                  v-model="template_data"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-col>
          <v-col>
            <v-row>
              <v-icon v-if="test_print_timer_running">mdi-timer</v-icon>
              <img v-if="template_content_rendering" :src="template_content_rendering"/>
            </v-row><v-row>
              <v-col>
                <v-btn  color="primary" x-large
                  @click="save_template">
                  <v-icon>mdi-content-save</v-icon>
                  SAVE
                </v-btn>
              </v-col><v-col>
                <v-btn  color="primary" x-large
                  @click="test_print">
                  <v-icon>mdi-test-tube</v-icon>
                  TEST
                </v-btn>
              </v-col>
            </v-row>
            <v-row>
              <v-textarea
                :label="template_action_title"
                :error-messages="template_action_error"
                :success="!template_action_error || true"
                rows=0
                :no-resize="true"
                :readonly="true"
              ></v-textarea>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </v-card>
</template>

<script>
import {get_logger} from '../../logger'
let log = get_logger('Admin/TemplateEditor.vue');

const parseJson = require('json-parse-better-errors')

import {lainuri_ws} from '../../lainuri'
import {Status, LEPrintTemplateList, LEPrintTemplateListResponse, LEPrintTemplateSave, LEPrintTemplateSaveResponse, LEPrintTestRequest, LEPrintTestResponse} from '../../lainuri_events.js'

import * as Timeout from '../../timeout_poller'

export default {
  name: 'TemplateEditor',
  created: function () {
    lainuri_ws.attach_event_listener(LEPrintTestResponse, this, function(event) {
      log.info(`[TemplateEditor.vue]:> Event 'LEPrintTestResponse' received.`);
      if (event.status === Status.SUCCESS) {
        this.$data.template_content_rendering = 'data:image/png;base64,' + event.image;
        this.$data.template_content_error = null
        this.$data.template_action_error = null;
        this.$data.template_action_title = "👍 LEPrintTestResponse"
      }
      else {
        this.$data.template_content_rendering = null
        this.$data.template_content_error = JSON.stringify(event.states)
        this.$data.template_action_error = JSON.stringify(event.states);
        this.$data.template_action_title = "👎 LEPrintTestResponse"
      }
    });
    lainuri_ws.attach_event_listener(LEPrintTemplateSaveResponse, this, function(event) {
      log.info(`[TemplateEditor.vue]:> Event 'LEPrintTemplateSaveResponse' received.`);
      if (event.status === Status.SUCCESS) {
        this.$data.template_action_error = null;
        this.$data.template_action_title = "👍 LEPrintTemplateSaveResponse"
      }
      else {
        this.$data.template_action_error = JSON.stringify(event.states);
        this.$data.template_action_title = "👎 LEPrintTemplateSaveResponse"
      }
    });
    lainuri_ws.attach_event_listener(LEPrintTemplateListResponse, this, function(event) {
      log.info(`[TemplateEditor.vue]:> Event 'LEPrintTemplateListResponse' received.`);
      if (event.status === Status.SUCCESS) {
        let templates_ordered = {}
        for (let t of event.templates) {
          if (! templates_ordered[t.type]) templates_ordered[t.type] = {}
          templates_ordered[t.type][t.locale_code] = t
        }
        this.$data.templates = templates_ordered
        // Trigger global reactivity
        for (let key in templates_ordered) {
          this.$set(this.templates, key, templates_ordered[key])
        }
        this.$data.template_content_error = null
        this.test_print();
      }
      else {
        this.$data.template_content_error = event.states
      }
    });
  },
  mounted: function () {
    lainuri_ws.dispatch_when_ready(new LEPrintTemplateList('client', 'server'));
  },
  beforeDestroy: function () {
    Timeout.terminate('TestPrintLazy');
    lainuri_ws.flush_listeners_for_component(this, this.$options.name);
  },
  data: () => ({
    tab: null,
    easy_mode: true,
    template_type: 'checkin',
    template_types: [
      'checkin', 'checkout',
    ],
    text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
    templates: {
      checkin: {
        'en': {"template": "loading {% today %}"},
      },
      checkout: {
        'en': {"template": "loading {% today %}"},
      },
    },
    template_content_rendering: null,
    template_content_error: null,
    template_data: JSON.stringify({
      "user": {
        "firstname": "Olli-Antti",
        "surname": "Kivilahti"
      },
      "items": [
        {
          "title": "Heroides",
          "author": "Publius Ovidius Naso",
          "item_barcode": "167N01010101"
        },
        {
          "title": "Pratima-nataka",
          "author": "Bhāsa",
          "item_barcode": "167N21212121"
        },
        {
          "title": "Drinking Alone by Moonlight",
          "author": "Li Bai",
          "item_barcode": "e00401003f382624"
        }
      ],
      "today": new Date().toLocaleDateString() + " " + new Date().toLocaleTimeString()
    }, null, 2),
    template_action_error: '',
    template_action_title: '',
    test_print_timer_running: false,
  }),
  computed: {
    template_active: function () {
      return this.templates[this.template_type][this.$appConfig.i18n.enabled_locales[this.tab]] || this.templates['checkin']['en']
    },
    template_content: {
      get: function () {
        return this.template_active.template
      },
      set: function (newVal) {
        this.template_active.template = newVal
      },
    },
    template_data_validation: function () {
      try {
        parseJson(this.template_data)
      } catch (e) {
        return e + ""
      }
      return null
    },
  },
  methods: {
    close_template_editor: function () {
      log.info('close_template_editor():>');
      this.$emit('close_template_editor')
    },
    maybe_lazy_test_print: function () {
      Timeout.terminate('TestPrintLazy')


      Timeout.start('TestPrintLazy', () => {
        this.$data.test_print_timer_running = false
        this.test_print();
      }, 1);
      this.$data.test_print_timer_running = true
    },
    save_template: function () {
      lainuri_ws.dispatch_event(new LEPrintTemplateSave(
        this.template_active.id,
        this.template_type,
        this.$appConfig.i18n.enabled_locales[this.tab],
        this.template_active.template, 'client', 'server'))
    },
    test_print: function () {
      lainuri_ws.dispatch_event(new LEPrintTestRequest(
        this.template_content,
        this.template_data,
        '',
        false, 'client', 'server'))
    },
  }
}
</script>

<style>
.template-editor {
  z-index: 100
}
.template-editor .v-textarea textarea {
  font-family: monospace;
  overflow: initial;
  font-size: 1rem;
  line-height: 1rem;
}
</style>
