import {run_test_suite} from './test_lainuri'

import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify';


import VueGlobalize from 'vue-globalize';
import {i18n_messages} from './i18n'

var Globalize = require( "globalize" );

Globalize.load(
//  require( "cldr-data/main/en/ca-gregorian" ),
  require( "cldr-data/supplemental/likelySubtags" ),
  require( "cldr-data/supplemental/plurals" ),
  require( "cldr-data/supplemental/ordinals" ),
//  require( "cldr-data/supplemental/timeData" ),
//  require( "cldr-data/supplemental/weekData" )
);
Globalize.loadMessages(i18n_messages)

Vue.use(VueGlobalize, {
  loadGlobalize: function(locale, categories, globalize, callback) {
      // make sure Globalize and the appropriate cldr data and messages
      // for the requested categories are loaded before creating the instance
      callback(new Globalize(locale));
  }
});

let test = 0;
if (test) {
  run_test_suite();
}
else {

  Vue.config.productionTip = false

  let vue = new Vue({
    vuetify,
    render: h => h(App)
  });
  vue.$setLocale('en')
  vue.$mount('#app')

}
