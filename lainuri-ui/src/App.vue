<template>
  <v-app>
    <v-app-bar
      app
      color="primary"
      dark
    >
      <div class="d-flex align-center">
        <v-img
          alt="Vuetify Logo"
          class="shrink mr-2"
          contain
          src="https://cdn.vuetifyjs.com/images/logos/vuetify-logo-dark.png"
          transition="scale-transition"
          width="40"
        />

        <v-img
          alt="Vuetify Name"
          class="shrink mt-1 hidden-sm-and-down"
          contain
          min-width="100"
          src="https://cdn.vuetifyjs.com/images/logos/vuetify-name-dark.png"
          width="100"
        />
      </div>

      <v-spacer></v-spacer>

      <v-btn
        href="https://github.com/vuetifyjs/vuetify/releases/latest"
        target="_blank"
        text
      >
        <span class="mr-2">Latest Release</span>
        <v-icon>mdi-open-in-new</v-icon>
      </v-btn>
    </v-app-bar>

    <v-content>
      <Main/>
    </v-content>

    <CheckOut v-if="app_mode === 'mode_checkout'" v-on:abort_user_login="abort_user_login" :user="user"/>
    <CheckIn  v-if="app_mode === 'mode_checkin'"  v-on:abort_user_login="abort_user_login"/>

    <div class="text-center">
      <v-btn v-if="app_mode === 'mode_main_menu'" id="checkout_mode_button" hover   color="secondary" dark v-on:click="enter_checkout_mode">LAINAA</v-btn>
      <v-btn v-if="app_mode === 'mode_main_menu'" id="checkin_mode_button" hover   color="primary" dark v-on:click="enter_checkin_mode">PALAUTA</v-btn>
    </div>


    <BottomMenu/>
  </v-app>
<!--
    <img alt="Vue logo" src="./assets/logo.png">

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
-->
</template>

<script>
import BottomMenu from './components/BottomMenu.vue'
import Main from './components/Main';
import CheckIn from './components/CheckIn.vue'
import CheckOut from './components/CheckOut.vue'

import {start_ws, lainuri_set_vue, lainuri_ws, send_user_logging_in, abort_user_login} from './lainuri'
import {LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed, LECheckOuting, LECheckOuted, LECheckOutFailed} from './lainuri_events'

function find_tag_by_key (tags, key, value) {
  for (tag in tags) {
    if (tag[key] === value) {
      return tag
    }
  }
  throw new Error(`Couldn't find a tag with '${key}'='${value}'`);
}

let preseed = 1;
export default {
  name: 'App',
  components: {
    CheckIn,
    CheckOut,
    Main,
    BottomMenu,
  },
  created: function () {
    lainuri_ws.attach_event_listener(LEUserLoggedIn, (event) => {
      console.log(`Received event '${LEUserLoggedIn.name}'`);
      this.$data.user = event;
    });
    lainuri_ws.attach_event_listener(LECheckOuted, (event) => {
      console.log(`Received event '${LECheckOuted.name}' for barcode='${event.barcode}'`);
      tag = find_tag_by_key(this.$data.rfid_tags_present, 'barcode', event.barcode)
      tag.checked_out = event.statuses
    });
    lainuri_ws.attach_event_listener(LECheckOutFailed, (event) => {
      console.log(`Received event '${LECheckOutFailed.name}' for barcode='${event.barcode}'`);
      tag = find_tag_by_key(this.$data.rfid_tags_present, 'barcode', event.barcode)
      tag.checked_out = event.statuses
    });

    if (preseed) {
      lainuri_ws.dispatch_event(
        new LEUserLoggedIn('Olli-Antti', 'Kivilahti', '167A01010101', 'server', 'client', 'user-logged-in-tzzzt')
      );
    }

    lainuri_set_vue(this);
    start_ws();

  },
  data: function () {
    return {
      activeBtn: 1,
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
      this.$data.user = {}
      abort_user_login();
    },
    checkout_item: function () {
      console.log("Checking out any available item");
      let not_checked_out_item;
      for (item_bib in this.$data.rfid_tags_present) {
        if (! item_bib.checked_out) {
          console.log(`Checking out any available item='${item_bib.barcode}'`);
          not_checked_out_item = item_bib;
          item_bib.checked_out = {status: 'pending'}
          break;
        }
      }
      lainuri.ws.dispatch_event(new LECheckOuting(item_bib.barcode, this.$data.user.borrowernumber, 'client', 'server'));
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
