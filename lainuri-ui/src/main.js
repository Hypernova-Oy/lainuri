import {run_test_suite} from './test_lainuri'

import Vue from 'vue'
import VueMaterial from 'vue-material'
import 'vue-material/dist/vue-material.min.css'
// Set theme
import 'vue-material/dist/theme/black-green-dark.css'
//import 'vue-material/dist/theme/black-green-light.css'
//import 'vue-material/dist/theme/default-dark.css'
//import 'vue-material/dist/theme/default.css'

import App from './App.vue'

let test = 0;
if (test) {
  run_test_suite();
}
else {

  Vue.use(VueMaterial)

  Vue.config.productionTip = false
  Vue.config.devtools = process.env.NODE_ENV === 'development'


  // change multiple options
  Vue.material = {
    ...Vue.material,
    // activeness of ripple effect
    ripple: true,

    theming: {},
    locale: {
      ...Vue.material.locale,

      // range for datepicker
      startYear: 1900,
      endYear: 2100,

      // date format for date picker
      dateFormat: 'dd-MM-yyyy',

      // i18n strings
      days: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
      shortDays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
      shorterDays: ['S', 'M', 'T', 'W', 'T', 'F', 'S'],
      months: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
      shortMonths: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'],
      shorterMonths: ['J', 'F', 'M', 'A', 'M', 'Ju', 'Ju', 'A', 'Se', 'O', 'N', 'D'],

      // `0` stand for Sunday, `1` stand for Monday
      firstDayOfAWeek: 1
    }
  }


  let vue = new Vue({
    render: h => h(App),
    methods: {
      debug (event) {
        window.console.log(event.target.name)
      }
    },
  }).$mount('#app')
}