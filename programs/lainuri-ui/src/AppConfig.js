import {get_logger} from './logger'
let log = get_logger('AppConfig.vue');

var Globalize = require( "globalize" );

import {lainuri_ws} from './lainuri'
import {Status, LEConfigGetpublic_Response} from './lainuri_events'

import lainuri_config_schema from './config_schema.json'

/**
 * Vue plugin install function
 */
export default function (Vue) {
  let vm = new Vue({
    name: 'AppConfig',
    created: function () {
      lainuri_ws.attach_event_listener(LEConfigGetpublic_Response, this, function(event) {
        log.info(`Event 'LEConfigGetpublic_Response' received.`);
        this.handle_new_app_configuration(event.config)
      });
    },
    beforeDestroy: function () {
      lainuri_ws.flush_listeners_for_component(this, this.$options.name);
    },

    data: function () {
      return {
        // see. config_schema.json for all configuration options
        app_config: {
          ui: {
            always_display_check_in_out_notification: true,
            images: {},
            main_menu_display_rfid_tags: true,
            session_inactivity_timeout_s: 120,
            popup_inactivity_timeout_s: 5,
            use_bookcovers: true,
            show_item_statuses: false,
          },
          i18n: {
            default_locale: 'en',
            enabled_locales: ['en'],
            messages: {},
          },
          devices: {
            "thermal-printer": {
              enabled: false,
            },
          },
        },
      }
    },
    methods: {
      handle_new_app_configuration: function (app_config) {
        log.debug('New configuration', app_config);
        if (this.$data.app_config.i18n.default_locale !== app_config.i18n.default_locale) this.set_locale(app_config.i18n.default_locale);

        if (app_config.ui.images) {
          app_config.ui.images = app_config.ui.images.reduce((acc, image_conf) => {acc[image_conf.position] = image_conf; return acc;}, {})
        }

        if (app_config.i18n.messages) {
          Globalize.loadMessages(app_config.i18n.messages)
        }

        // Trigger global reactivity
        for (let key in app_config) {
          this.$set(this.app_config, key, app_config[key])
        }
      },
      set_locale: function (lang_2_char) {
        log.info(`New language '${lang_2_char}'`)
        lang_2_char = lang_2_char.substring(0,2)
        this.$setLocale(lang_2_char)
        this.$data.app_config.i18n.default_locale = lang_2_char
        return lang_2_char
      },
      get_image_overload: function (position) {
        if (this.app_config.ui.images && this.app_config.ui.images[position]) {
          return 'image_overloads/'+position+'.png'
        }
        return 'images/'+position+'.png'
      },
    }
  });
  Vue.prototype.$lainuriConfigSchema = lainuri_config_schema
  Vue.prototype.$appConfig = vm.$data.app_config
  Vue.prototype.$appConfigSetLocale = vm.set_locale
  Vue.prototype.$appConfigGetImageOverload = vm.get_image_overload
}
