import {run_test_suite} from './test_lainuri'

import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify';

let test = 0;
if (test) {
  run_test_suite();
}
else {

  Vue.config.productionTip = false

  let vue = new Vue({
    vuetify,
    render: h => h(App)
  }).$mount('#app')
}
