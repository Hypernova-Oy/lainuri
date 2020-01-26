<template>
  <v-container centered>
    <v-card ripple raised>
      <v-row>
        <v-col>
          <v-card-title>PALAUTETAAN</v-card-title>
        </v-col>
        <v-col>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              v-on:click="stop_checking_in"
              large color="secondary"
            >
              LOPETA
            </v-btn>
            <v-btn
              v-on:click="stop_checkin_in_and_get_receipt"
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
              <v-toolbar-title>Lainasi</v-toolbar-title>
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
              <v-toolbar-title>Lainattavana</v-toolbar-title>
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
              <v-toolbar-title>Virheet</v-toolbar-title>
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

import {find_tag_by_key} from '../helpers'
import {start_ws, lainuri_set_vue, lainuri_ws, send_user_logging_in, abort_user_login} from '../lainuri'
import {LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed, LECheckIn, LECheckInComplete, LECheckInFailed, LECheckOuting, LECheckOuted, LECheckOutFailed, LEBarcodeRead, LEPrintRequest, LEPrintResponse} from '../lainuri_events'

let emited = 0
export default {
  name: 'CheckIn',
  components: {
    ItemCard,
  },
  props: {
    rfid_tags_present: Array,
  },
  created: function () {
    lainuri_ws.attach_event_listener(LECheckOuted, this, (event) => {
      console.log(`Received event '${LECheckOuted.name}' for barcode='${event.item_barcode}'`);
      let tag = find_tag_by_key(this.$data.rfid_tags_present, 'item_barcode', event.item_barcode)
      tag.checked_out_statuses = event.statuses
      tag.checkout_status = event.statuses.status
      this.items_checked_out_successfully.append(tag);
    });
    lainuri_ws.attach_event_listener(LECheckOutFailed, this, (event) => {
      console.log(`Received event '${LECheckOutFailed.name}' for barcode='${event.item_barcode}'`);
      let tag = find_tag_by_key(this.$data.rfid_tags_present, 'item_barcode', event.item_barcode)
      tag.checked_out_statuses = event.statuses
      tag.checkout_status = event.statuses.status
      this.items_checked_out_failed.append(tag);
    });
    lainuri_ws.attach_event_listener(LEBarcodeRead, this, (event) => {
      console.log(`Received event '${LEBarcodeRead.name}' for barcode='${event.item_barcode}'`);
      if (this.user) {
        this.checkout_item(event);
      }
      else {
        console.error(`Received event '${LEBarcodeRead.name}' for barcode='${event.item_barcode}', but no user logged in?`);
      }
    });
    lainuri_ws.attach_event_listener(LEBarcodeRead, this, (event) => {
      console.log(`Received event '${LEBarcodeRead.name}' for barcode='${event.item_barcode}'`);
      this.checkin_item(event);
    });
    lainuri_ws.attach_event_listener(LEPrintResponse, this, (event) => {
      console.log(`Received event '${LEPrintResponse.name}'`);
      this.$data.receipt_printing = false;
      this.stop_checking_in();
    });
  },
  beforeDestroy: function () {
    lainuri_ws.flush_listeners_for_component(this, this.$name);
  },
  methods: {
    stop_checking_in: function () {
      console.log("Stopped checking in");
      this.$emit('stop_checking_in');
    },
    stop_checkin_in_and_get_receipt: function () {
      console.log("Stopping checking in and getting a receipt");
      this.print_receipt();
      //this.stop_checking_out(); // The kill signal is given when the receipt printing confirmation is received from the server
    },
    print_receipt: function () {
      console.log("Printing receipt");
      this.$data.receipt_printing = true;
      lainuri_ws.dispatch_event(
        new LEPrintRequest(
          this.$data.items_checked_in_successfully,
        ),
      );
    },
    checkin_item: function (item_bib) {
      console.log(`Checking in item '${item_bib.item_barcode}'`);
      item_bib.checked_in_statuses = {status: 'pending'}
      item_bib.checkin_status = item_bib.checked_out_statuses.status
      lainuri_ws.dispatch_event(new LECheckIn(item_bib.item_barcode, this.$data.user.user_barcode, 'client', 'server'));
    },
  },
  data: () => ({
    receipt_printing: false,
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
