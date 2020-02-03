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
      <v-col v-if="items_checked_in_successfully.length"
        :cols="column_width"
      >
        <v-card
          min-width="300"
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
                v-for="(item) in items_checked_in_successfully"
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

      <v-col v-if="rfid_tags_present.reduce((red, bib) => red === true || !(bib.status) || bib.status === 'pending', false)"
        :cols="column_width"
      >
        <v-card
          min-width="300"
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
                <ItemCard v-if="!item.status || (item.status !== 'failed' && item.status !== 'success')" v-bind:key="item.item_barcode" :item_bib="item"/>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-col>

      <v-col v-if="items_checked_in_failed.length"
        :cols="column_width"
      >
        <v-card
          min-width="300"
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
                v-for="(item) in items_checked_in_failed"
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

    <PrintNotification :receipt_printing="receipt_printing"
      v-on:close_notification="print_receipt_complete"
    />
    <v-overlay :value="overlay_notifications.length">
      <OverlayNotification
        :item_bib="overlay_notifications[0]"
        v-on:close_notification="close_notification"
      />
    </v-overlay>

  </v-container>
</template>

<script>
import ItemCard from '../components/ItemCard.vue'
import OverlayNotification from '../components/OverlayNotification.vue'
import PrintNotification from '../components/PrintNotification.vue'

import {find_tag_by_key, splice_bib_item_from_array} from '../helpers'
import {start_ws, lainuri_set_vue, lainuri_ws} from '../lainuri'
import {LERFIDTagsNew, LECheckIn, LECheckInComplete, LEBarcodeRead, LEPrintRequest, LEPrintResponse} from '../lainuri_events'

let emited = 0
export default {
  name: 'CheckIn',
  components: {
    ItemCard,
    OverlayNotification,
    PrintNotification,
  },
  props: {
    rfid_tags_present: Array,
  },
  created: function () {
    lainuri_ws.attach_event_listener(LECheckInComplete, this, function(event) {
      console.log(`Received event '${LECheckInComplete.name}' for barcode='${event.item_barcode}'`);
      let tag = find_tag_by_key(this.rfid_tags_present, 'item_barcode', event.item_barcode)
      if (!tag) {
        tag = find_tag_by_key(this.barcodes_read, 'item_barcode', event.item_barcode)
        splice_bib_item_from_array(this.barcodes_read, 'item_barcode', event.item_barcode);
      }
      if (!tag) throw new Error(`Couldn't find a tag with 'item_barcode'='${event.item_barcode}'`);
      tag.states = event.states
      tag.status = event.status

      if (event.status === 'success') {
        this.items_checked_in_successfully.unshift(tag);
      }
      else {
        this.items_checked_in_failed.unshift(tag);
      }

      if (Object.keys(event.states).length) {
        this.overlay_notifications.push(tag);
      }
    });
    lainuri_ws.attach_event_listener(LEBarcodeRead, this, function(event) {
      console.log(`Received event '${LEBarcodeRead.name}' for barcode='${event.barcode}'`);
      if (this.user.user_barcode) {
        this.barcodes_read.push(event.tag)
        this.check_in_item(event.tag);
      }
      else {
        console.error(`Received event '${LEBarcodeRead.name}' for barcode='${event.barcode}', but no user logged in?`);
      }
    });
    lainuri_ws.attach_event_listener(LERFIDTagsNew, this, function(event) {
      console.log(`[${this.$options.name}]:> Event '${LERFIDTagsNew.name}' triggered. New RFID tags:`, event.tags_new);
      event.tags_new.forEach((item_bib) => {
        let tags_present_item_bib = find_tag_by_key(this.rfid_tags_present, 'item_barcode', item_bib.item_barcode)
        if (! tags_present_item_bib) {
          console.error(`[${this.$options.name}]:> Event '${LERFIDTagsNew.name}':> New item '${item_bib.item_barcode}' detected, but it is not in the this.$props.rfid_tags_present -list (length='${this.rfid_tags_present.length}')`);
        }
        this.check_in_item(tags_present_item_bib);
      });
    });
    lainuri_ws.attach_event_listener(LEPrintResponse, this, function(event) {
      console.log(`Received event '${LEPrintResponse.name}'`);
      if (this.receipt_printing) {this.print_receipt_complete(event);}
      else {console.error(`Received event '${LEPrintResponse.name}' but not printing a receipt. User race condition maybe?`)}
    });
  },
  mounted: function () {
    this.start_checking_in();
  },
  beforeDestroy: function () {
    lainuri_ws.flush_listeners_for_component(this, this.$options.name);
    this.items_checked_in_failed = []
    this.items_checked_in_successfully = []
    this.barcodes_read = []
  },
  computed: {
    column_width: function () {
      let visible_columns = 0;
      if (this.items_checked_in_failed.length) {
        visible_columns++;
        console.log(`column_width():> this.items_checked_in_failed visible`)
      }
      if (this.items_checked_in_successfully.length) {
        visible_columns++;
        console.log(`column_width():> this.items_checked_in_successfully visible`)
      }
      if (this.rfid_tags_present.reduce((red, bib) => red === true || !(bib.status) || bib.status === 'pending', false)) {
        visible_columns++;
        console.log(`column_width():> this.rfid_tags_present visible`)
      }
      return (12 / visible_columns);
    }
  },
  methods: {
    stop_checking_in: function () {
      console.log("Stopped checking out");
      this.$data.user = {};
      this.$emit('stop_checking_in');
    },
    stop_checkin_in_and_get_receipt: function () {
      console.log("Stopping checking out and getting a receipt");
      this.print_receipt();
      //this.stop_checking_in(); // The kill signal is given when the receipt printing confirmation is received from the server
    },
    start_checking_in: function (event) {
      console.log(`Started checking out. Items present '${this.rfid_tags_present.length}'`);
      for (let i in this.rfid_tags_present) {
        let item_bib = this.rfid_tags_present[i];
        this.check_in_item(item_bib, 1000*i);
      }
    },
    check_in_item: function (item_bib, delay) {
      console.log(`Checking out item '${item_bib.item_barcode}'`);
      if (! item_bib.checked_in) {
        item_bib.states = {status: 'pending'}
        item_bib.status = 'pending'
        //window.setTimeout(() =>
          lainuri_ws.dispatch_event(new LECheckIn(item_bib.item_barcode, 'client', 'server'))
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
          'check-in',
          this.$data.items_checked_in_successfully,
          {},
        ),
      );
    },
    print_receipt_complete: function (event) {
      this.$data.receipt_printing = false;
      if (event) {
        this.$emit('exception', event.status.exception);
      }
      this.stop_checking_in();
    },
    close_notification: function () {
      console.log("Closing notification");
      this.$data.overlay_notifications.shift();
    },
  },
  data: () => ({
    receipt_printing: false,
    barcodes_read: [],
    overlay_notifications: [
/*      {
        item_barcode: '167N00770111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
        status: 'error',
        states: {
          no_item: '167N00770111',
        },
      },
      {
        item_barcode: '167N00770111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
        status: 'success',
        states: {
          not_checked_out: '1',
        },
      },*/
    ],
    items_checked_in_successfully: [
/*      {
        item_barcode: '167N00770111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        status: 'success',
      },*/
    ],
    items_checked_in_failed: [
/*      {
        item_barcode: '167N00660001',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
        status: 'error',
      },
      {
        item_barcode: '167N00550111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        status: 'error',
      },
      {
        item_barcode: '167N00440001',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
        status: 'error',
      },
      {
        item_barcode: '167N00110111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        status: 'error',
      },
      {
        item_barcode: '167N00220001',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
        status: 'error',
      },
      {
        item_barcode: '167N00330111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        status: 'error',
      },*/
    ],
  }),
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
