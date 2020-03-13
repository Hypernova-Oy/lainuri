<template>
  <v-app>

    <v-app-bar
      app
      color="primary"
      dark
      :height="app_mode !== 'mode_main_menu' ? 64 : 400"
    >
      <div class="align-center">
        <v-img
          v-if="app_mode !== 'mode_main_menu'"
          alt="Logo"
          src="/xamk-logo-small.png"
          width="150"
          v-bind:css="false"
        />
      </div>
      <div class="align-center">
        <v-img
          v-if="app_mode === 'mode_main_menu'"
          alt="Logo"
          src="/xamk-logo-big.png"
          width="150"
          v-bind:css="false"
        />
      </div>

      <v-spacer></v-spacer>


      <v-btn v-if="app_mode === 'mode_main_menu' || app_mode === 'mode_checkout'"
        id="checkout_mode_button"
        :width="app_mode === 'mode_checkout' ? 800 : 350"
        hover   color="secondary" dark x-large
        v-on:click="enter_checkout_mode"
      ><h1>{{t('App/Check_out')}}</h1></v-btn>
      <v-btn v-if="app_mode === 'mode_main_menu' || app_mode === 'mode_checkin'"
        id="checkin_mode_button"
        :width="app_mode === 'mode_checkin' ? 800 : 350"
        :color="app_mode === 'mode_checkin' ? 'secondary' : 'primary'"
        hover dark x-large
        v-on:click="enter_checkin_mode"
      ><h1>{{t('App/Check_in')}}</h1></v-btn>

      <v-spacer></v-spacer>

      <v-col cols="1">
        <LanguagePicker/>
      </v-col>

    </v-app-bar>
    <div id="app-bar-spacer-helper"
      v-if="app_mode === 'mode_main_menu'"
      style="height: 336px;"
    >
    </div>
    <v-container fluid max-height="800">
      <StatusBar :status="status"/>
      <Exception v-if="exceptions.length"
        :exception="exceptions[0]" :exceptions_count="exceptions.length"
        v-on:exception_close="exceptions.shift()"
      />
      <MainMenuView v-if="app_mode === 'mode_main_menu'"
        :rfid_tags_present="rfid_tags_present"
        v-on:exception="show_exception"
      />
      <CheckOut v-if="app_mode === 'mode_checkout'"
        :rfid_tags_present="rfid_tags_present"
        v-on:stop_checking_out="stop_checking_out"
        v-on:exception="show_exception"
      />
      <CheckIn v-if="app_mode === 'mode_checkin'"
        :rfid_tags_present="rfid_tags_present"
        v-on:stop_checking_in="stop_checking_in"
        v-on:exception="show_exception"
      />
    </v-container>

    <v-footer
      app
      color="blue-grey"
      class="white--text"
    >
      Hypernova Linux Perl Python wiringPi WebSocket CernOHL Vuetify ECMAScript6 RFID ESC/POS Ansible ISO18000-3M3 Git <span class="footer-tech-name" @click="repl_active = true">RTTTL</span>
      <v-spacer></v-spacer>
      <span>&copy; 2020</span>
    </v-footer>

    <v-snackbar
      v-model="repl_active"
      :timeout="0"
    >
      <v-textarea
        name="input-7-1"
        label="REPL here"
        placeholder="This is evaled in the context of the 'App.vue'-component"
        v-model="repl"
        clearable="true"
        outlined="true"
        dark
      ></v-textarea>
      <v-btn
        color="red"
        text
        @click="repl_execute()"
      >
        Run
      </v-btn>
      <v-btn
        color="pink"
        text
        @click="repl_active = false"
      >
        Close
      </v-btn>
    </v-snackbar>
  </v-app>
</template>

<script>
import {get_logger} from './logger'
let log = get_logger('App.vue');

import Globalize from 'globalize'

import BottomMenu from './components/BottomMenu.vue'
import Exception from './components/Exception.vue'
import ItemCard from './components/ItemCard'
import LanguagePicker from './components/LanguagePicker.vue'
import CheckIn from './components/CheckIn.vue'
import CheckOut from './components/CheckOut.vue'
import MainMenuView from './components/MainMenuView.vue'
import StatusBar from './components/StatusBar.vue'

import {ItemBib} from './item_bib'
import {splice_bib_item_from_array} from './helpers'
import {start_ws, lainuri_set_vue, lainuri_ws, abort_user_login} from './lainuri'
import {Status, LERFIDTagsNew, LERFIDTagsLost, LERFIDTagsPresent, LEServerConnected, LEServerDisconnected, LEServerStatusRequest, LEServerStatusResponse, LEUserLoginComplete} from './lainuri_events'


let shared = {
  item_barcode: '167N00000111',
  book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
  title: 'Dummies for Grenades',
  author: 'Olli-Antti Kivilahti',
  status: 'success',
};


let preseed = 1;
export default {
  name: 'App',
  components: {
    CheckIn,
    CheckOut,
    Exception,
    LanguagePicker,
    MainMenuView,
    StatusBar,
  },
  created: function () {
    lainuri_ws.attach_event_listener(LERFIDTagsNew, this, function(event) {
      log.info(`Event '${LERFIDTagsNew.name}' received. New RFID tags (${event.tags_new.length}):`, event.tags_new, event.tags_present);
      event.tags_new.forEach((item_bib) => {
        this.rfid_tags_present.push(new ItemBib(item_bib));
      });
    });
    lainuri_ws.attach_event_listener(LERFIDTagsLost, this, function(event) {
      log.info(`Event '${LERFIDTagsLost.name}' received. Lost RFID tags (${event.tags_lost.length}):`, event.tags_lost, event.tags_present);
      event.tags_lost.forEach((item_bib) => {
        splice_bib_item_from_array(this.rfid_tags_present, 'item_barcode', item_bib.item_barcode);
      });
    });
    lainuri_ws.attach_event_listener(LERFIDTagsPresent, this, function(event) {
      log.info(`Event '${LERFIDTagsPresent.name}' received. Present RFID tags (${event.tags_present.length}):`, event.tags_present);
      this.rfid_tags_present = event.tags_present.reduce((reducer, elem) => {reducer.push(new ItemBib(elem)); return reducer}, []);
    });
    lainuri_ws.attach_event_listener(LEServerStatusResponse, this, function(event) {
      log.info(`Event '${LEServerStatusResponse.name}' received.`);
    });
    lainuri_ws.attach_event_listener(LEServerConnected, this, function(event) {
      log.info(`Event '${LEServerConnected.name}' received.`);
      this.$data.status.server_connected = Status.SUCCESS;
    });
    lainuri_ws.attach_event_listener(LEServerDisconnected, this, function(event) {
      log.info(`Event '${LEServerDisconnected.name}' received.`);
      this.$data.status.server_connected = Status.ERROR;
    });
    if (!preseed) {
      lainuri_ws.attach_event_listener(LEServerConnected, this, (event) => {
        log.info(`PRESEEDING!! Received '${LEServerConnected.name}'`);
        window.setTimeout(() => lainuri_ws.dispatch_event(
          new LEUserLoginComplete('Olli-Antti', 'Kivilahti', '2600104874', Status.SUCCESS, {}, 'server', 'client')
        ), 4000);
      });
    }
  },

  mounted: function () {
    log.info('mounted()');
    try {
      start_ws();
    } catch (e) {
      log.fatal(`start_ws() :> ${e}`);
    }
  },

  beforeDestroy: function () {
    lainuri_ws.flush_listeners_for_component(this, this.$options.name);
    lainuri_ws.ws.close();
  },

  data: function () {
    return {
      name: 'Vue.js',
      app_mode: 'mode_main_menu',
      exceptions: [],
      //exceptions: [{exception: "Traceback (most recent call last):\n  File \"/home/kivilahtio/work/Lainuri/RFID/python/lainuri/websocket_handlers/printer.py\", line 15, in print_receipt\n    borrower = koha_api.get_borrower(event.user_barcode)\n  File \"/home/kivilahtio/work/Lainuri/RFID/python/lainuri/koha_api/__init__.py\", line 169, in get_borrower\n    return self._expected_one_list_element(payload, f\"user_barcode='{user_barcode}'\")\n  File \"/home/kivilahtio/work/Lainuri/RFID/python/lainuri/koha_api/__init__.py\", line 93, in _expected_one_list_element\n    raise NoResults(error_msg)\nlainuri.exceptions.NoResults: user_barcode='None'\n"}],
      rfid_tags_present: [],
      /*rfid_tags_present: [
        {
          item_barcode: '167N00000001',
          book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
          title: 'Grenades for Dummies',
          author: 'Olli-Antti Kivilahti',
          status: 'pending',
        },{
          item_barcode: '167N11111111',
          book_cover_url: 'https://synergydental.org.uk/wp-content/uploads/2019/06/Synergy-Favicon-90x90.png',
          title: 'Books for Dummies',
          author: 'Olli-Antti Kivilahti',
        },{
          item_barcode: '167222222222',
          book_cover_url: 'https://papasfishandchips.com/wp-content/uploads/2018/03/FAVICON1-1.png',
          title: 'Fa ces for Dummies',
          author: 'Olli-Antti Kivilahti',
        },
        shared,
      ],*/
      bottom_bar_view: undefined,
      bottom_bar_view_debug: false,
      bottom_bar_view_config: false,

      status: {
        server_connected: Status.ERROR,
        printer_off: Status.SUCCESS,
        printer_paper_low: Status.SUCCESS,
        printer_paper_out: Status.SUCCESS,
        printer_receipt_not_torn: Status.SUCCESS,
        rfid_reader_off: Status.SUCCESS,
        barcode_reader_off: Status.SUCCESS,
        ils_connection_status: Status.SUCCESS,
      },

      repl_active: false,
      repl: '',
    }
  },
  // define methods under the `methods` object
  methods: {
    enter_checkout_mode: function () {
      this.app_mode = 'mode_checkout';
      log.info(`Entering 'mode_checkout'`);
    },
    enter_checkin_mode: function () {
      this.app_mode = 'mode_checkin';
      log.info(`Entering 'mode_checkin'`);
    },
    enter_main_menu: function () {
      this.app_mode = 'mode_main_menu';
      this.rfid_tags_present.forEach(bib_item => {
        ItemBib.prototype.flush_statuses.call(bib_item)
      });
    },
    stop_checking_out: function () {
      this.enter_main_menu();
    },
    stop_checking_in: function () {
      this.enter_main_menu();
    },
    show_exception: function (event) {
      this.$data.exceptions.push(event);
    },
    set_language: function (lang_2_char) {
      this.$setLocale(lang_2_char)
      this.$data.active_language_2_char = lang_2_char
    },


    repl_execute: function () {
      let resp = eval(this.$data.repl);
      console.log(resp);
    },
  }
}
</script>

<style>
body {
  height: 1920px;
  width: 1080px;
}

.item_scrollview {
  max-height: 1500px;
  overflow: auto;
}

#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  border-color: #2c3e50;
  border-width: 5px;
}

#checkout_mode_button {
  height: 100%;
}

#checkin_mode_button {
  height: 100%;
}

button {
  font-size: 10em;
}

.bottom-bar-viewport {
  width: 100%;
  height: 200px;
  overflow: hidden;
  border: 1px solid rgba(#000, .26);
  background: rgba(#000, .06);
}

.lang-menu-open-container {
  position: relative;
}
.lang-menu-open-container .lang-menu-dropdown-icon {
  position: absolute;
  bottom: 10px;
  left: 50px;
}
.footer-tech-name {
  padding-left: 5px;
}
</style>
