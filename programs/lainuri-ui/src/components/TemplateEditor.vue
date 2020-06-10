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
          v-for="(item, i) in template_types"
          :key="i"
          @click="template_type = item"
        >
          <v-list-item-title>{{ item }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>

    <v-toolbar-title>Template editor - {{ template_type }}</v-toolbar-title>

      <v-spacer></v-spacer>
      <v-switch v-model="easy_mode" label="Easy mode"></v-switch>
      <template v-slot:extension>
        <v-tabs
          v-model="tab"
          align-with-title
        >
          <v-tabs-slider color="yellow"></v-tabs-slider>
          <v-tab v-for="item in items" :key="item">
            {{ item }}
          </v-tab>
        </v-tabs>
      </template>
    </v-toolbar>

    <v-tabs-items v-model="tab">
      <v-tab-item
        v-for="item in items"
        :key="item"
      >
      </v-tab-item>
    </v-tabs-items>
    <v-card flat>
      <v-card-text v-text="templates[template_type][items[tab]]"></v-card-text>

      <v-container class="grey lighten-5">
        <v-row>
          <v-col>
            <v-row>
              <v-col>
                <v-textarea
                  label="Template"
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
              <v-textarea v-if="template_content_error"
                label="Template error"
                auto-grow
                v-model="template_content_error"
              ></v-textarea>
            </v-row>
            <v-row>
              <v-textarea
                label="Template data validation"
                auto-grow
                v-model="template_data_validation"
              ></v-textarea>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </v-card>
</template>

<script>
import {get_logger} from '../logger'
let log = get_logger('TemplateEditor.vue');

const parseJson = require('json-parse-better-errors')

import {lainuri_ws} from '../lainuri'
import {Status, LEPrintTemplateList, LEPrintTemplateListResponse, LEPrintTemplateSave, LEPrintTemplateSaveResponse, LEPrintTestRequest, LEPrintTestResponse} from '../lainuri_events.js'

import * as Timeout from '../timeout_poller'

export default {
  name: 'TemplateEditor',
  created: function () {
    lainuri_ws.attach_event_listener(LEPrintTestResponse, this, function(event) {
      log.info(`[TemplateEditor.vue]:> Event 'LEPrintTestResponse' received.`);
      if (event.status === Status.SUCCESS) {
        this.$data.template_content_rendering = 'data:image/png;base64,' + event.image;
        this.$data.template_content_error = null
      }
      else {
        this.$data.template_content_rendering = null
        this.$data.template_content_error = event.states
      }
    });
    lainuri_ws.attach_event_listener(LEPrintTemplateListResponse, this, function(event) {
      log.info(`[TemplateEditor.vue]:> Event 'LEPrintTemplateListResponse' received.`);
      if (event.status === Status.SUCCESS) {
        this.$data.templates = event.templates
        this.$data.template_content_error = null
      }
      else {
        this.$data.template_content_error = event.states
      }
    });
  },
  mounted: function () {
    lainuri_ws.dispatch_event(new LEPrintTemplateList('client', 'server')) // Seed the initial templates from server
  },
  beforeDestroy: function () {
    Timeout.terminate();
  },
  data () {
    return {
      tab: null,
      easy_mode: true,
      template_type: 'checkin',
      template_types: [
        'checkin', 'checkout',
      ],
      items: [
        'fi', 'en', 'ru', 'sv', 'de',
      ],
      text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
      templates: {
        checkin: {
          'fi': "asdasdasd",
          'en': "asdasdasdasdasdasd",
        },
        checkout: {
          'fi': "asdasdasd123123",
          'en': "asdasdasdasdasdasd123123",
        },
      },
      template_content: "",
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
      test_print_timer_running: false,
    }
  },
  computed: {
    template_data_validation: function () {
      try {
        parseJson(this.template_data)
      } catch (e) {
        return e
      }
      return '👍'
    },
  },
  methods: {
    maybe_lazy_test_print: function () {
      Timeout.terminate()
      Timeout.start(() => {
        this.$data.test_print_timer_running = false
        this.test_print();
      }, 1);
      this.$data.test_print_timer_running = true
    },
    test_print: function () {
      lainuri_ws.dispatch_event(new LEPrintTestRequest(this.template_content, this.template_data, '', false, 'client', 'server'))
    },
  }
}
</script>

<style>
.template-editor textarea {
  font-family: monospace;
}
</style>
