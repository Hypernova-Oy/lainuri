<template>
  <v-container centered>
    <v-card ripple raised>
      <v-row>
        <v-col>
          <v-card-title v-if="! user.user_barcode">LUE KIRJASTOKORTTI</v-card-title>
          <v-card-title v-if="user.user_barcode">MOI {{user.firstname}}!</v-card-title>
        </v-col>
        <v-col>
          <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn
              v-on:click="abort_user_login"
              v-if="!user.user_barcode"
              large color="secondary"
            >
              PALAA
            </v-btn>

            <v-btn
              v-on:click="stop_checkin_out"
              v-if="user.user_barcode"
              large color="secondary"
            >
              LOPETA
            </v-btn>
            <v-btn
              v-on:click="stop_checkin_out_and_get_receipt"
              v-if="user.user_barcode"
              large color="secondary"
            >
              LOPETA + KUITTI
            </v-btn>
          </v-card-actions>
        </v-col>
      </v-row>
    </v-card>


      <v-row dense>
        <v-col v-if="items_checked_out_successfully" cols="4">
          <v-card
            v-if="items_checked_out_successfully.length"
            min-width="345"
            class="mx-auto"
          >
            <v-app-bar
              color="primary"
              dark
            >
              <v-toolbar-title>LAINASI</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-app-bar>

            <v-container class="item_scrollview">
              <v-row dense>
                <v-col
                  v-for="(item) in items_checked_out_successfully"
                  :key="item.item_barcode"
                  align="center"
                  justify="center"
                >
                  <ItemCard v-bind:key="item.item_barcode" :item_bib="item"/>
                </v-col>
              </v-row>
            </v-container>
          </v-card>
        </v-col>

        <v-col cols="4">
          <v-card
            v-if="rfid_tags_present.length"
            min-width="345"
            class="mx-auto"
          >
            <v-app-bar
              color="primary"
              dark
            >
              <v-toolbar-title>JONOSSA</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-app-bar>

            <v-container class="item_scrollview">
              <v-row dense>
                <v-col
                  v-for="(item) in rfid_tags_present"
                  :key="item.item_barcode"
                  align="center"
                  justify="center"
                >
                  <ItemCard v-if="!item.checkout_status" v-bind:key="item.item_barcode" :item_bib="item"/>
                </v-col>
              </v-row>
            </v-container>
          </v-card>
        </v-col>

        <v-col cols="4">
          <v-card
            v-if="items_checked_out_failed.length"
            min-width="345"
            class="mx-auto"
          >
            <v-app-bar
              color="primary"
              dark
            >
              <v-toolbar-title>VIRHEET</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-app-bar>

            <v-container class="item_scrollview">
              <v-row dense>
                <v-col
                  v-for="(item) in items_checked_out_failed"
                  :key="item.item_barcode"
                  align="center"
                  justify="center"
                >
                  <ItemCard v-bind:key="item.item_barcode" :item_bib="item"/>
                </v-col>
              </v-row>
            </v-container>
          </v-card>
        </v-col>

      </v-row>
  </v-container>
</template>

<script>
import ItemCard from '../components/ItemCard.vue'

import {find_tag_by_key} from '../helpers'
import {start_ws, lainuri_set_vue, lainuri_ws, send_user_logging_in, abort_user_login} from '../lainuri'
import {LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed, LECheckOuting, LECheckOuted, LECheckOutFailed} from '../lainuri_events'


export default {
  name: 'CheckOut',
  components: {
    ItemCard,
  },
  props: {
    user: Object,
    rfid_tags_present: Array,
  },
  created: function () {
    lainuri_ws.attach_event_listener(LEUserLoginFailed, function(event) {
      console.log(`Event '${LEUserLoginFailed.name}' received.`);
      this.$data.user = {}
      this.$data.app_mode = 'mode_main_menu';
    });
    lainuri_ws.attach_event_listener(LEUserLoginAbort, function(event) {
      console.log(`Event '${LEUserLoginAbort.name}' received.`);
      this.$data.user = {}
      this.$data.app_mode = 'mode_main_menu';
    });
    lainuri_ws.attach_event_listener(LEUserLoggedIn, (event) => {
      console.log(`Received event '${LEUserLoggedIn.name}'`);
      this.$data.user = event;
      this.$data.app_mode = 'mode_checkout';
      this.start_checking_out();
    });
    lainuri_ws.attach_event_listener(LECheckOuted, (event) => {
      console.log(`Received event '${LECheckOuted.name}' for barcode='${event.item_barcode}'`);
      let tag = find_tag_by_key(this.$data.rfid_tags_present, 'item_barcode', event.item_barcode)
      tag.checked_out_statuses = event.statuses
      tag.checkout_status = event.statuses.status
    });
    lainuri_ws.attach_event_listener(LECheckOutFailed, (event) => {
      console.log(`Received event '${LECheckOutFailed.name}' for barcode='${event.item_barcode}'`);
      let tag = find_tag_by_key(this.$data.rfid_tags_present, 'item_barcode', event.item_barcode)
      tag.checked_out_statuses = event.statuses
      tag.checkout_status = event.statuses.status
    });
  },
  methods: {
    abort_user_login: function () {
      console.log("abort_user_login in CheckOut")
      this.$emit('abort_user_login');
    },
    stop_checking_out: function () {
      console.log("Stopped checking out");
      this.$emit('stop_checking_out');
    },
    stop_checkin_out_and_get_receipt: function () {
      console.log("Stopping checking out and getting a receipt");
      this.stop_checking_in();
    },
    start_checking_out: function () {
      console.log("Started checking out");

      this.checkout_item();
    },
    checkout_item: function () {
      console.log("Checking out any available item. Items present " + this.$data.rfid_tags_present.length);
      for (let i in this.$data.rfid_tags_present) {
        let item_bib = this.$data.rfid_tags_present[i]
        if (! item_bib.checked_out) {
          console.log(`Checking out any available item='${item_bib.item_barcode}'`);
          item_bib.checked_out_statuses = {status: 'pending'}
          item_bib.checkout_status = item_bib.checked_out_statuses.status
          lainuri_ws.dispatch_event(new LECheckOuting(item_bib.item_barcode, this.$data.user.user_barcode, 'client', 'server'));
          break;
        }
      }
    },
  },
  data: () => ({
    items_checked_out_successfully: [
      {
        item_barcode: '167N00000111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        checkout_status: 'success',
      },
    ],
    items_checked_out_failed: [
      {
        item_barcode: '167N00000001',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
        checkout_status: 'error',
      },
      {
        item_barcode: '167N00000111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        checkout_status: 'error',
      },
      {
        item_barcode: '167N00000001',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
        checkout_status: 'error',
      },
      {
        item_barcode: '167N00000111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        checkout_status: 'error',
      },
      {
        item_barcode: '167N00000001',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
        checkout_status: 'error',
      },
      {
        item_barcode: '167N00000111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        checkout_status: 'error',
      },
    ],
  }),
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
