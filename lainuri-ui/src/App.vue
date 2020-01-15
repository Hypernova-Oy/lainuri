<template>
  <div id="app">
    <img alt="Vue logo" src="./assets/logo.png">
    <ul id="container_item_carousel">
      <ItemCard v-for="tag in rfid_tags_present" v-bind:key="tag.barcode" :item_bib="tag"/>
    </ul>
    <CheckOut v-if="app_mode === 'mode_checkout'" v-on:abort_user_login="abort_user_login"/>
    <CheckIn  v-if="app_mode === 'mode_checkin'"  v-on:abort_user_login="abort_user_login"/>
    <md-button v-if="app_mode === 'mode_main_menu'" id="checkout_mode_button" class="md-raised md-primary md-display-4" v-on:click="enter_checkout_mode">LAINAA</md-button>
    <md-button v-if="app_mode === 'mode_main_menu'" id="checkin_mode_button" class="md-raised md-accent md-display-4" v-on:click="enter_checkin_mode">PALAUTA</md-button>

    <div class="bottom-bar-viewport">
      <md-content v-if="bottom_bar_view == 'debug'">{{barcode_read}}<br/>{{rfid_tags_present}}</md-content>
      <md-content v-if="bottom_bar_view == 'config'">Koti<br/>Sivu</md-content>
      <md-bottom-bar class="md-accent" md-type="shift">
        <md-bottom-bar-item id="bottom-bar-debug-view" @click="bottom_bar_view='debug'" md-label="Debug" md-icon="developer_board"></md-bottom-bar-item>
        <md-bottom-bar-item id="bottom-bar-hide-view" @click="bottom_bar_view=undefined" md-label="Hide" md-icon="remove"></md-bottom-bar-item>
        <md-bottom-bar-item id="bottom-bar-configure-view" @click="bottom_bar_view='config'" md-label="Configure" md-icon="widgets"></md-bottom-bar-item>
      </md-bottom-bar>
    </div>
  </div>
</template>

<script>
import CheckIn from './components/CheckIn.vue'
import CheckOut from './components/CheckOut.vue'
import ItemCard from './components/ItemCard.vue'
import {start_ws, lainuri_set_vue, lainuri_ws, send_user_logging_in, abort_user_login} from './lainuri'
import {LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed} from './lainuri_events'


export default {
  name: 'app',
  components: {
    CheckIn,
    CheckOut,
    ItemCard,
  },
  created: function () {
    this.$data.barcode_read = 'HASDHASHDAHSD';

    lainuri_set_vue(this);
    start_ws();

  },
  data: function () {
    return {
      name: 'Vue.js',
      app_mode: 'mode_main_menu',
      user: {},
      barcode_read: '',
      rfid_tags_present: [],
      bottom_bar_view: undefined,
      bottom_bar_view_debug: false,
      bottom_bar_view_config: false,
    }
  },
  // define methods under the `methods` object
  methods: {
    enter_checkout_mode: function () {
      this.app_mode = 'mode_checkout';
      console.log("Entering 'mode_checkout'");
      this.barcode_read = '1234';
      send_user_logging_in();
    },
    enter_checkin_mode: function () {
      this.app_mode = 'mode_checkin';
      console.log("Entering 'mode_checkin'");
      this.barcode_read = '4321';
    },
    abort_user_login: function () {
      this.app_mode = 'mode_main_menu';
      abort_user_login();
    },
    bottom_bar_view_toggle: function (event) {
      console.log(`bottom_bar_view_toggle event='${event}'`, event)
      this.bottom_bar_view_debug = false;
      this.bottom_bar_view_config = false;
    },
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

#checkout_mode_button {
  width: 49%;
  height: 400px;
}

#checkin_mode_button {
  width: 49%;
  height: 400px;
}

.md-card {
  width: 320px;
  margin: 4px;
  display: inline-block;
  vertical-align: top;
}

.bottom-bar-viewport {
  width: 100%;
  height: 200px;
  overflow: hidden;
  border: 1px solid rgba(#000, .26);
  background: rgba(#000, .06);
}
.md-bottom-bar {
  position: relative;
  bottom: 0px;
}

</style>
