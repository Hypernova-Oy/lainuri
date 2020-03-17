import {get_logger} from './logger'
let log = get_logger('AppConfig.vue');

import {lainuri_ws} from './lainuri'
import {Status, LEConfigGetpublic_Response} from './lainuri_events'

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
        app_config: {
          default_language: 'en',
          use_bookcovers: true,
          dateformat: '%d.%m.%Y',
        },
      }
    },
    methods: {
      handle_new_app_configuration: function (app_config) {
        log.debug('New configuration', app_config);
        if (this.$data.app_config.default_language !== app_config.default_language) this.set_locale(app_config.default_language);
        this.$data.app_config = app_config
        Vue.prototype.$appConfig = this.$data.app_config // Trigger global reactivity
      },
      set_locale: function (lang_2_char) {
        log.info(`New language '${lang_2_char}'`)
        lang_2_char = lang_2_char.substring(0,2)
        this.$setLocale(lang_2_char)
        this.$data.app_config.default_language = lang_2_char
      },
    }
  });
  Vue.prototype.$appConfig = vm.$data.app_config
  Vue.prototype.$appConfigSetLocale = vm.set_locale
}
