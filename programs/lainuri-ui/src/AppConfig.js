import {get_logger} from './logger'
let log = get_logger('AppConfig.vue');

var Globalize = require( "globalize" );
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
        // see. config_schema.json for all configuration options
        app_config: {
          ui: {
            images: {},
            use_bookcovers: true,
          },
          i18n: {
            default_locale: 'en',
            enabled_locales: ['en'],
            messages: {},
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

        this.$data.app_config = app_config
        Vue.prototype.$appConfig = this.$data.app_config // Trigger global reactivity
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
  Vue.prototype.$appConfig = vm.$data.app_config
  Vue.prototype.$appConfigSetLocale = vm.set_locale
  Vue.prototype.$appConfigGetImageOverload = vm.get_image_overload
}
