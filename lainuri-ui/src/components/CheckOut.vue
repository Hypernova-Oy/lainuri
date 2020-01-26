<template>
  <v-container centered>
    <v-card ripple raised>
      <v-row>
        <v-col>
          <v-card-title v-if="! is_user_logged_in">LUE KIRJASTOKORTTI</v-card-title>
          <v-card-title v-if="is_user_logged_in">MOI {{user.firstname}} ({{user.user_barcode}})!</v-card-title>
          <v-card v-if="user_login_error" raised color="error">KIRJAUTUMINEN EPÄONNISTUI</v-card>
        </v-col>
        <v-col>
          <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn
              v-on:click="abort_user_login"
              v-if="!is_user_logged_in"
              large color="secondary"
            >
              PALAA
            </v-btn>

            <v-btn
              v-on:click="stop_checking_out"
              v-if="is_user_logged_in"
              large color="secondary"
            >
              LOPETA
            </v-btn>
            <v-btn
              v-on:click="stop_checkin_out_and_get_receipt"
              v-if="is_user_logged_in"
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
                <ItemCard v-if="!item.checkout_status || (item.checkout_status !== 'failed' && item.checkout_status !== 'success')" v-bind:key="item.item_barcode" :item_bib="item"/>
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

    <v-overlay :value="receipt_printing">
      <ArrowSliding/>
    </v-overlay>

  </v-container>
</template>

<script>
import ItemCard from '../components/ItemCard.vue'
import ArrowSliding from '../components/ArrowSliding.vue'

import {find_tag_by_key} from '../helpers'
import {start_ws, lainuri_set_vue, lainuri_ws, send_user_logging_in, abort_user_login} from '../lainuri'
import {LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed, LERFIDTagsNew, LECheckOuting, LECheckOuted, LECheckOutFailed, LEBarcodeRead, LEPrintRequest, LEPrintResponse} from '../lainuri_events'


export default {
  name: 'CheckOut',
  components: {
    ItemCard,
    ArrowSliding,
  },
  props: {
    rfid_tags_present: Array,
  },
  created: function () {
    send_user_logging_in();

    lainuri_ws.attach_event_listener(LEUserLoginFailed, this, function(event) {
      console.log(`Event '${LEUserLoginFailed.name}' received.`);
      this.user_login_failed(event);
    });
    lainuri_ws.attach_event_listener(LEUserLoggedIn, this, (event) => {
      console.log(`Received event '${LEUserLoggedIn.name}'`);
      if (! this.is_user_logged_in) {
        this.user_login_success(event);
      }
      else {
        console.error(`User '${this.$data.user.user_barcode}' already logged in? Login attempt from user '${event.user_barcode}'`);
      }
    });
    lainuri_ws.attach_event_listener(LECheckOuted, this, function(event) {
      console.log(`Received event '${LECheckOuted.name}' for barcode='${event.item_barcode}'`);
      let tag = find_tag_by_key(this.rfid_tags_present, 'item_barcode', event.item_barcode)
      tag.checked_out_statuses = event.statuses
      tag.checkout_status = event.statuses.status
      this.items_checked_out_successfully.unshift(tag);
    });
    lainuri_ws.attach_event_listener(LECheckOutFailed, this, function(event) {
      console.log(`Received event '${LECheckOutFailed.name}' for barcode='${event.item_barcode}'`);
      let tag = find_tag_by_key(this.rfid_tags_present, 'item_barcode', event.item_barcode)
      tag.checked_out_statuses = event.statuses
      if (! tag.checked_out_statuses) tag.checked_out_statuses = event.exception
      tag.checkout_status = event.statuses.status
      this.items_checked_out_failed.unshift(tag);
    });
    lainuri_ws.attach_event_listener(LEBarcodeRead, this, function(event) {
      console.log(`Received event '${LEBarcodeRead.name}' for barcode='${event.item_barcode}'`);
      if (this.user) {
        this.checkout_item(event);
      }
      else {
        console.error(`Received event '${LEBarcodeRead.name}' for barcode='${event.item_barcode}', but no user logged in?`);
      }
    });
    lainuri_ws.attach_event_listener(LERFIDTagsNew, this, function(event) {
      console.log(`[${this.$options.name}]:> Event '${LERFIDTagsNew.name}' triggered. New RFID tags:`, event.tags_new);
      if (this.is_user_logged_in) {
        event.tags_new.forEach((item_bib) => {
          let tags_present_item_bib = find_tag_by_key(this.rfid_tags_present, 'item_barcode', item_bib.item_barcode)
          if (! tags_present_item_bib) {
            console.error(`[${this.$options.name}]:> Event '${LERFIDTagsNew.name}':> New item '${item_bib.item_barcode}' detected, but it is not in the this.$props.rfid_tags_present -list (length='${this.rfid_tags_present.length}')`);
          }
          this.checkout_item(tags_present_item_bib);
        });
      }
    });
    lainuri_ws.attach_event_listener(LEPrintResponse, this, function(event) {
      console.log(`Received event '${LEPrintResponse.name}'`);
      this.$data.receipt_printing = false;
      this.$emit('exception', event.status.exception);
      this.stop_checking_out();
    });
  },
  beforeDestroy: function () {
    lainuri_ws.flush_listeners_for_component(this, this.$options.name);
    this.items_checked_out_failed = []
    this.items_checked_out_successfully = []
  },
  computed: {
    is_user_logged_in: function () {
      return (this.$data.user.user_barcode) ? true : false;
    },
  },
  methods: {
    user_login_failed: function (error) {
      this.$data.user = {};
      this.$data.user_login_error = event;
      this.$emit('exception', event)
    },
    user_login_success: function (event) {
      this.$data.user = event;
      this.$data.user_login_error = null;
      this.start_checking_out(event);
    },
    abort_user_login: function () {
      console.log("abort_user_login in CheckOut");
      lainuri_ws.dispatch_event(new LEUserLoginAbort('client', 'server'));
      this.stop_checking_out();
    },
    stop_checking_out: function () {
      console.log("Stopped checking out");
      this.$data.user = {};
      this.$data.user_login_error = null;
      this.$emit('stop_checking_out');
    },
    stop_checkin_out_and_get_receipt: function () {
      console.log("Stopping checking out and getting a receipt");
      this.print_receipt();
      //this.stop_checking_out(); // The kill signal is given when the receipt printing confirmation is received from the server
    },
    start_checking_out: function (event) {
      console.log(`Started checking out. Items present '${this.rfid_tags_present.length}'`);
      for (let i in this.rfid_tags_present) {
        let item_bib = this.rfid_tags_present[i];
        this.checkout_item(item_bib, 1000*i);
      }
    },
    checkout_item: function (item_bib, delay) {
      console.log(`Checking out item '${item_bib.item_barcode}'`);
      if (! item_bib.checked_out) {
        item_bib.checked_out_statuses = {status: 'pending'}
        item_bib.checkout_status = 'pending'
        //window.setTimeout(() =>
          lainuri_ws.dispatch_event(new LECheckOuting(item_bib.item_barcode, this.$data.user.user_barcode, 'client', 'server'))
        //, delay);
      }
      else {
        console.error(`Checking out item '${item_bib.item_barcode}', but it is already checked out?`);
      }
    },
    print_receipt: function () {
      console.log("Printing receipt");
      this.$data.receipt_printing = true;
      lainuri_ws.dispatch_event(
        new LEPrintRequest(
          this.$data.items_checked_out_successfully,
          this.$data.user.user_barcode,
        ),
      );
    },
  },
  data: () => ({
    receipt_printing: false,
    user: Object,
    user_login_error: null,
    items_checked_out_successfully: [],
    items_checked_out_failed: [],
/*      {
        item_barcode: '167N00000123',
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
        exception: 'Not available for anything',
      },
      {
        item_barcode: '167N00000111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        checkout_status: 'error',
        exception: 'Not available for anything',
      },
      {
        item_barcode: '167N00000321',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
        checkout_status: 'error',
        exception: 'Not available for anything',
      },
      {
        item_barcode: '167N00333111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        checkout_status: 'error',
        exception: 'Not available for anything',
      },
      {
        item_barcode: '167N00333001',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
        checkout_status: 'error',
      },
      {
        item_barcode: '167N00223111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        checkout_status: 'error',
      },*/
  }),
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
