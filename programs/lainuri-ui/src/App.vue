<template>
  <v-app>

    <v-app-bar class="app-navigation-bar"
      app
      color="primary"
      dark
      :height="app_mode !== 'mode_main_menu' ? 96 : 400"
    >
      <div class="align-center">
        <v-img
          v-if="app_mode !== 'mode_main_menu'"
          alt="Logo"
          :src="$appConfigGetImageOverload('logo-small')"
          width="150"
          v-bind:css="false"
        />
      </div>
      <div class="align-center">
        <v-img
          v-if="app_mode === 'mode_main_menu'"
          alt="Logo"
          :src="$appConfigGetImageOverload('logo-big')"
          width="150"
          v-bind:css="false"
        />
      </div>

      <v-spacer></v-spacer>


      <v-btn v-if="app_mode === 'mode_main_menu' || app_mode === 'mode_checkout'"
        id="checkout_mode_button"
        :width="app_mode === 'mode_checkout' ? 770 : 325"
        hover   color="secondary" dark x-large
        v-on:click="enter_checkout_mode"
      ><h1>{{(app_mode === 'mode_main_menu') ? t('App/Check_out') : t('CheckOut/Checking_out')}}</h1></v-btn>
      <v-spacer></v-spacer>
      <v-btn v-if="app_mode === 'mode_main_menu' || app_mode === 'mode_checkin'"
        id="checkin_mode_button"
        :width="app_mode === 'mode_checkin' ? 770 : 325"
        :color="app_mode === 'mode_checkin' ? 'secondary' : 'primary'"
        hover dark x-large
        v-on:click="enter_checkin_mode"
      ><h1>{{(app_mode === 'mode_main_menu') ? t('App/Check_in') : t('CheckIn/Checking_in')}}</h1></v-btn>
      <v-btn v-if="app_mode === 'mode_admin_menu'"
        id="admin_mode_button"
        :width="app_mode === 'mode_admin_menu' ? 770 : 325"
        :color="app_mode === 'mode_admin_menu' ? 'secondary' : 'primary'"
        hover dark x-large
      ><h1>Admin</h1></v-btn>

      <v-spacer></v-spacer>

      <LanguagePicker/>

    </v-app-bar>
    <div id="app-bar-spacer-helper"
      v-bind:class="{
        main_menu_view: app_mode === 'mode_main_menu',
        other_view: app_mode !== 'mode_main_menu',
      }"
    >
    </div>

    <AdminMenu
      v-if="app_mode === 'mode_admin_menu'"
      v-on:close_admin_menu="enter_main_menu"
      v-on:enable_repl="repl_active = true"
      v-on:exception="show_exception"
    />

    <v-container fluid max-height="800">
      <StatusBar/>
      <transition-group name="fade" mode="out-in" appear tag="span" class="exceptions-listing">
        <Exception v-for="(exc) in exceptions" :key="exc.eid"
          :exception="exc" :exceptions_count="exceptions.length" :eid="exc.eid"
          v-on:exception_close="close_exception(exc)"
        />
      </transition-group>
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

    <v-snackbar
      v-model="repl_active"
      :timeout="0"
    >
      <v-textarea
        name="input-7-1"
        label="REPL here"
        placeholder="This is evaled in the context of the 'App.vue'-component"
        v-model="repl"
        clearable
        outlined
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

import AdminMenu from './components/Admin/AdminMenu.vue'
import BottomMenu from './components/BottomMenu.vue'
import Exception from './components/Exception.vue'
import ItemCard from './components/ItemCard'
import LanguagePicker from './components/LanguagePicker.vue'
import CheckIn from './components/CheckIn.vue'
import CheckOut from './components/CheckOut.vue'
import MainMenuView from './components/MainMenuView.vue'
import StatusBar from './components/StatusBar.vue'

import {ItemBib} from './item_bib'
import {splice_bib_item_from_array, find_tag_by_key} from './helpers'
import {start_ws, lainuri_set_vue, lainuri_ws, abort_user_login} from './lainuri'
import {Status, LEAdminModeEnter, LEAdminModeLeave, LEException, LEItemBibFullDataResponse, LERFIDTagsNew, LERFIDTagsLost, LERFIDTagsPresentRequest, LERFIDTagsPresent} from './lainuri_events'


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
    AdminMenu,
    CheckIn,
    CheckOut,
    Exception,
    LanguagePicker,
    MainMenuView,
    StatusBar,
  },
  created: function () {
    lainuri_ws.attach_event_listener(LEAdminModeEnter, this, function(event) {
      log.info(`Event 'LEAdminModeEnter' received.`);
      this.app_mode = 'mode_admin_menu'
    });
    lainuri_ws.attach_event_listener(LEAdminModeLeave, this, function(event) {
      log.info(`Event 'LEAdminModeLeave' received.`);
      this.app_mode = 'mode_main_menu'
    });
    lainuri_ws.attach_event_listener(LEException, this, function(event) {
      log.info(`Event 'LEException' received. (${event.type}):`, event);
      this.show_exception(event);
    });
    lainuri_ws.attach_event_listener(LERFIDTagsNew, this, function(event) {
      log.info(`Event 'LERFIDTagsNew' received. New RFID tags (${event.tags_new.length}):`, event.tags_new, event.tags_present);

      if (event.status !== Status.SUCCESS) {
        this.show_exception(event);
        return;
      }

      event.tags_new.forEach((item_bib) => {
        this.rfid_tags_present.push(new ItemBib(item_bib));
      });
    });
    lainuri_ws.attach_event_listener(LERFIDTagsLost, this, function(event) {
      log.info(`Event 'LERFIDTagsLost' received. Lost RFID tags (${event.tags_lost.length}):`, event.tags_lost, event.tags_present);
      event.tags_lost.forEach((item_bib) => {
        splice_bib_item_from_array(this.rfid_tags_present, 'item_barcode', item_bib.item_barcode);
      });
    });
    lainuri_ws.attach_event_listener(LERFIDTagsPresent, this, function(event) {
      log.info(`Event 'LERFIDTagsPresent' received. Present RFID tags (${event.tags_present.length}):`, event.tags_present);
      this.rfid_tags_present = event.tags_present.reduce((reducer, elem) => {reducer.push(new ItemBib(elem)); return reducer}, []);
    });
    lainuri_ws.attach_event_listener(LEItemBibFullDataResponse, this, function(event) {
      //if (this.$data.app_mode !== "mode_main_menu") return; // Other modes handle this event in their own handlers.
      log.info(`Event 'LEItemBibFullDataResponse'`);
      for (let item_bib_data of event.item_bibs) {
        let tags_present_item_bib_and_i = find_tag_by_key(this.rfid_tags_present, 'item_barcode', item_bib_data.item_barcode)
        if (! tags_present_item_bib_and_i) continue; // It is ok to not have a matching ItemBib since it could be removed while the supplementary data is being received.
        let item_bib = tags_present_item_bib_and_i[0];
        if (item_bib_data.status === Status.SUCCESS) { // ItemBib FullData fetching is a non-critical part of the transaction, so it's successful status doesn't define the transaction's status
          delete(item_bib_data.status);
          delete(item_bib_data.states);
        }
        Object.assign(item_bib, item_bib_data)
      }
    });

    try {
      start_ws();
    } catch (e) {
      log.fatal(`start_ws() :> ${e}`);
    }

  },
  mounted: function () {

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

      repl_active: false,
      repl: '',
    }
  },
  // define methods under the `methods` object
  methods: {
    enter_checkout_mode: function () {
      log.info(`Entering 'mode_checkout'`);
      this.app_mode = 'mode_checkout';
    },
    enter_checkin_mode: function () {
      log.info(`Entering 'mode_checkin'`);
      this.app_mode = 'mode_checkin';
    },
    enter_main_menu: function () {
      log.info(`Entering 'mode_main_menu'`);
      this.app_mode = 'mode_main_menu';
      // Flush RFID tags present from the Lainuri-server
      this.rfid_tags_present = [];
      lainuri_ws.dispatch_event(new LERFIDTagsPresentRequest());
    },
    stop_checking_out: function () {
      this.enter_main_menu();
    },
    stop_checking_in: function () {
      this.enter_main_menu();
    },
    show_exception: function (event) {
      event.eid = Math.random()
      this.$data.exceptions.push(event);
    },
    close_exception: function (exception) {
      /* Due to a race condition of multiple timers ending when closing multiple Exception notifications, we cannot simply shift the array,
        we need to splice the correct item, as the shifted array index might not be the one that actually times out, even if they are in
        the correct order of timing out. */
      let idx = this.$data.exceptions.findIndex((el) => el === exception);
      this.$data.exceptions.splice(idx,1);
    },
    repl_execute: function () {
      let resp = eval(this.$data.repl);
      console.log(resp);
    },
  }
}
</script>

<style>
html {
  scrollbar-width: none;
}
html::-webkit-scrollbar {
  display: none;
}
body {
  height: 1920px;
  width: 1080px;
  scrollbar-width: none;
}
body::-webkit-scrollbar {
  display: none;
}
#app {
  height: 100%;
  width: 100%;
  scrollbar-width: none;
}
#app::-webkit-scrollbar {
  display: none;
}

* {
  cursor: none !important
}

span.exceptions-listing {
  display: flex;
  flex-direction: column-reverse;
}

.item_scrollview {
  max-height: 1500px;
  overflow: auto;
}
.v-card__title {
  word-break: normal;
}

#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  border-color: #2c3e50;
  border-width: 5px;
}
#app-bar-spacer-helper.main_menu_view {
  height: 400px;
}
#app-bar-spacer-helper.other_view {
  height: 96px;
}

.app-navigation-bar button.v-size--x-large {
  font-size: 1.3em;
}
.app-navigation-bar #checkout_mode_button {
  height: 100%;
}

.app-navigation-bar #checkin_mode_button {
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


/* Global animation/transition styles */
.fade-enter-active, .fade-leave-active {
  transition: opacity .3s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}

</style>
