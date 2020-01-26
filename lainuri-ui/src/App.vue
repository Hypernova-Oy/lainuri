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
          alt="Logo"
          src="/xamk.png"
          width="150"

        />
      </div>

      <v-spacer></v-spacer>


      <v-btn v-if="app_mode === 'mode_main_menu' || app_mode === 'mode_checkout'"
        id="checkout_mode_button"
        :width="app_mode === 'mode_checkout' ? 800 : 400"
        hover   color="secondary" dark
        v-on:click="enter_checkout_mode"
        v-on:exception="show_exception"
      >LAINAA</v-btn>
      <v-btn v-if="app_mode === 'mode_main_menu' || app_mode === 'mode_checkin'"
        id="checkin_mode_button"
        :width="app_mode === 'mode_checkin' ? 800 : 400"
        :color="app_mode === 'mode_checkin' ? 'secondary' : 'primary'"
        hover dark
        v-on:click="enter_checkin_mode"
        v-on:exception="show_exception"
      >PALAUTA</v-btn>

      <v-spacer></v-spacer>


    </v-app-bar>
    <div id="app-bar-spacer-helper"
      v-if="app_mode === 'mode_main_menu'"
      style="height: 336px;"
    >
    </div>
    <v-container fluid max-height="800">
      <Exception v-if="exception" :except_str="exception" v-on:exception_close="exception = null"/>
      <MainMenuView v-if="app_mode === 'mode_main_menu'"
        :rfid_tags_present="rfid_tags_present"
      />
      <CheckOut v-if="app_mode === 'mode_checkout'"
        :rfid_tags_present="rfid_tags_present"
        v-on:stop_checking_out="stop_checking_out"
      />
      <CheckIn v-if="app_mode === 'mode_checkin'"
        :rfid_tags_present="rfid_tags_present"
        v-on:stop_checking_in="stop_checking_in"
      />
    </v-container>

    <v-footer
      app
      color="blue-grey"
      class="white--text"
    >
      <BottomMenu/>
      <span>Vuetify</span>
      <v-spacer></v-spacer>
      <span>&copy; 2019</span>
    </v-footer>
  </v-app>
</template>

<script>
import BottomMenu from './components/BottomMenu.vue'
import Exception from './components/Exception.vue'
import ItemCard from './components/ItemCard'
import CheckIn from './components/CheckIn.vue'
import CheckOut from './components/CheckOut.vue'
import MainMenuView from './components/MainMenuView.vue'

import {find_tag_by_key, splice_bib_item_from_array} from './helpers'
import {start_ws, lainuri_set_vue, lainuri_ws, send_user_logging_in, abort_user_login} from './lainuri'
import {LERFIDTagsNew, LERFIDTagsLost, LERFIDTagsPresent, LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed, LECheckOuting, LECheckOuted, LECheckOutFailed} from './lainuri_events'
import { LEServerConnected } from './lainuri_events';

let shared = {
          item_barcode: '167N00000111',
          book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
          title: 'Dummies for Grenades',
          author: 'Olli-Antti Kivilahti',
          checkout_status: 'success',
        };


let preseed = 1;
export default {
  name: 'App',
  components: {
    CheckIn,
    CheckOut,
    BottomMenu,
    Exception,
    MainMenuView,
  },
  created: function () {
    lainuri_ws.attach_event_listener(LERFIDTagsNew, this, function(event) {
      console.log(`[${this.$options.name}]:> Event '${LERFIDTagsNew.name}' triggered. New RFID tags (${event.tags_new.length}):`, event.tags_new, event.tags_present);
      event.tags_new.forEach((item_bib) => {
        //item_bib.checkout_status = 'new'
        this.rfid_tags_present.push(item_bib);
      });
    });
    lainuri_ws.attach_event_listener(LERFIDTagsLost, this, function(event) {
      console.log(`[${this.$options.name}]:> Event '${LERFIDTagsLost.name}' triggered. Lost RFID tags (${event.tags_lost.length}):`, event.tags_lost, event.tags_present);
      event.tags_lost.forEach((item_bib) => {
        splice_bib_item_from_array(this.rfid_tags_present, 'item_barcode', item_bib.item_barcode);
      });
    });
    lainuri_ws.attach_event_listener(LERFIDTagsPresent, this, function(event) {
      console.log(`[${this.$options.name}]:> Event '${LERFIDTagsPresent.name}' triggered. Present RFID tags (${event.tags_present.length}):`, event.tags_present);
      event.tags_present.forEach((item_bib) => {
        //item_bib.checkout_status = 'present'
      });
      this.rfid_tags_present = event.tags_present;
    });
    if (preseed) {
      lainuri_ws.attach_event_listener(LEServerConnected, this, (event) => {
        console.log(`PRESEEDING!! Received '${LEServerConnected.name}'`);
        window.setTimeout(() => lainuri_ws.dispatch_event(
          new LEUserLoggedIn('Olli-Antti', 'Kivilahti', '2600104874', 'server', 'client')
        ), 4000);
      });
    }

    lainuri_set_vue(this);
  },

  mounted: function () {
    console.log("App.vue - mounted()");
    start_ws();
  },

  data: function () {
    return {
      activeBtn: 1,
      name: 'Vue.js',
      app_mode: 'mode_main_menu',
      barcode_read: '',
      //exception: null,
      exception: "Traceback (most recent call last):\n  File \"/home/kivilahtio/work/Lainuri/RFID/python/lainuri/websocket_handlers/printer.py\", line 15, in print_receipt\n    borrower = koha_api.get_borrower(event.user_barcode)\n  File \"/home/kivilahtio/work/Lainuri/RFID/python/lainuri/koha_api/__init__.py\", line 169, in get_borrower\n    return self._expected_one_list_element(payload, f\"user_barcode='{user_barcode}'\")\n  File \"/home/kivilahtio/work/Lainuri/RFID/python/lainuri/koha_api/__init__.py\", line 93, in _expected_one_list_element\n    raise NoResults(error_msg)\nlainuri.exceptions.NoResults: user_barcode='None'\n",
      rfid_tags_present: [
        {
          item_barcode: '167N00000001',
          book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
          title: 'Grenades for Dummies',
          author: 'Olli-Antti Kivilahti',
          checkout_status: 'pending',
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
      ],
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
    },
    enter_checkin_mode: function () {
      this.app_mode = 'mode_checkin';
      console.log("Entering 'mode_checkin'");
    },
    enter_main_menu: function () {
      this.app_mode = 'mode_main_menu';
      this.rfid_tags_present.forEach(bib_item => {
        bib_item.checked_out_statuses = null
        bib_item.checkout_status = 'present'
      });
    },
    stop_checking_out: function () {
      this.enter_main_menu();
    },
    stop_checking_in: function () {
      this.enter_main_menu();
    },
    show_exception: function (exception) {
      this.$data.exception = exception;
    }
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



.bottom-bar-viewport {
  width: 100%;
  height: 200px;
  overflow: hidden;
  border: 1px solid rgba(#000, .26);
  background: rgba(#000, .06);
}

</style>
