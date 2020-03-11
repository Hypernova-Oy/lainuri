<template>
  <v-container centered>
    <v-card ripple raised>
      <v-row>
        <v-col>
          <v-card-title v-if="! is_user_logged_in">{{t('CheckOut/Read_library_card')}}</v-card-title>
          <v-card-title v-if="is_user_logged_in">{{t('CheckOut/Hi_user!', {user: user.firstname})}}</v-card-title>
        </v-col>
        <v-col>
          <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn
              v-on:click="abort_user_login"
              v-if="!is_user_logged_in"
              x-large color="secondary"
            >
              {{t('CheckOut/Return')}}
            </v-btn>

            <v-btn
              v-on:click="stop_checking_out"
              v-if="is_user_logged_in"
              x-large color="secondary"
            >
              {{t('CheckOut/Stop')}}
            </v-btn>
            <v-btn
              v-on:click="stop_checkin_out_and_get_receipt"
              v-if="is_user_logged_in"
              x-large color="secondary"
            >
              {{t('CheckOut/Stop+Receipt')}}
            </v-btn>
          </v-card-actions>
        </v-col>
      </v-row>
    </v-card>

    <v-row dense>
      <v-col v-if="Object.keys(items_checked_out_successfully).length"
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
            <v-toolbar-title>{{t('CheckOut/Your_Check_outs')}}</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-app-bar>

          <v-container class="item_scrollview">
            <v-row dense>
              <v-col
                v-for="(item_bib) in items_checked_out_successfully"
                :key="item_bib.item_barcode"
                align="center"
                justify="center"
              >
                <ItemCard v-bind:key="item_bib.item_barcode" :item_bib="item_bib"/>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-col>

      <v-col v-if="rfid_tags_present_filtered"
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
            <v-toolbar-title>{{t('CheckOut/In_Queue')}}</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-app-bar>

          <v-container class="item_scrollview">
            <v-row dense>
              <v-col
                v-for="(item_bib) in rfid_tags_present_filtered"
                :key="item_bib.item_barcode"
                align="center"
                justify="center"
              >
                <ItemCard v-bind:key="item_bib.item_barcode" :item_bib="item_bib"/>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-col>

      <v-col v-if="Object.keys(items_checked_out_failed).length"
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
            <v-toolbar-title>{{t('CheckOut/Errors')}}</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-app-bar>

          <v-container class="item_scrollview">
            <v-row dense>
              <v-col
                v-for="(item_bib) in items_checked_out_failed"
                :key="item_bib.item_barcode"
                align="center"
                justify="center"
              >
                <ItemCard v-bind:key="item_bib.item_barcode" :item_bib="item_bib"/>
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
        :mode="'checkout'"
        v-on:close_notification="close_notification"
      />
    </v-overlay>

  </v-container>
</template>

<script>
import ItemCard from '../components/ItemCard.vue'
import OverlayNotification from '../components/OverlayNotification.vue'
import PrintNotification from '../components/PrintNotification.vue'

import {find_tag_by_key} from '../helpers'
import {ItemBib} from '../item_bib'
import {lainuri_ws, send_user_logging_in} from '../lainuri'
import {Status, LEUserLoginComplete, LEUserLoggingIn, LEUserLoginAbort, LERFIDTagsNew, LECheckOut, LECheckOutComplete, LEBarcodeRead, LEPrintRequest, LEPrintResponse, LESetTagAlarm, LESetTagAlarmComplete} from '../lainuri_events'


export default {
  name: 'CheckOut',
  components: {
    ItemCard,
    OverlayNotification,
    PrintNotification,
  },
  props: {
    rfid_tags_present: Array,
  },
  created: function () {
    send_user_logging_in();

    lainuri_ws.attach_event_listener(LEUserLoginComplete, this, (event) => {
      console.log(`[${this.$options.name}]:> Received event '${LEUserLoginComplete.name}'`);
      if (event.status === Status.SUCCESS) {
        if (! this.is_user_logged_in) {
          this.user_login_success(event);
        }
        else {
          console.error(`User '${this.$data.user.user_barcode}' already logged in? Login attempt from user '${event.user_barcode}'`);
        }
      }
      else {
        this.user_login_failed(event);
      }
    });
    lainuri_ws.attach_event_listener(LECheckOutComplete, this, function(event) {
      console.log(`[${this.$options.name}]:> Received event '${LECheckOutComplete.name}' for barcode='${event.item_barcode}'`);
      this.check_out_complete(event);
    });
    lainuri_ws.attach_event_listener(LEBarcodeRead, this, function(event) {
      console.log(`[${this.$options.name}]:> Event '${LEBarcodeRead.name}' for barcode='${event.barcode}'`);
      if (this.is_user_logged_in) {
        this.start_or_continue_transaction(event.tag)
      }
      else {
        console.error(`Received event '${LEBarcodeRead.name}' for barcode='${event.barcode}', but no user logged in?`);
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
          this.start_or_continue_transaction(tags_present_item_bib);
        });
      }
      else {
        console.log(`[${this.$options.name}]:> Event '${LERFIDTagsNew.name}' triggered. User not logged in yet.`);
      }
    });
    lainuri_ws.attach_event_listener(LESetTagAlarmComplete, this, function(event) {
      console.log(`[${this.$options.name}]:> Event '${LESetTagAlarmComplete.name}' for item_barcode='${event.item_barcode}'`);
      this.set_rfid_tag_alarm_complete(event);
    });
    lainuri_ws.attach_event_listener(LEPrintResponse, this, function(event) {
      console.log(`[${this.$options.name}]:> Event '${LEPrintResponse.name}'`);
      if (this.receipt_printing) {this.print_receipt_complete(event);}
      else {console.error(`Received event '${LEPrintResponse.name}' but not printing a receipt. User race condition maybe?`)}
    });
  },
  beforeDestroy: function () {
    lainuri_ws.flush_listeners_for_component(this, this.$options.name);
    this.items_checked_out_failed = {}
    this.items_checked_out_successfully = {}
  },
  computed: {
    is_user_logged_in: function () {
      return (this.$data.user.user_barcode) ? true : false;
    },
    rfid_tags_present_filtered: function () {
      return this.rfid_tags_present.filter((item_bib) => [Status.PENDING, Status.NOT_SET].includes(item_bib.status))
    },
    column_width: function () {
      let visible_columns = 0;
      if (Object.keys(this.items_checked_out_failed).length) {
        visible_columns++;
        console.log(`column_width():> this.items_checked_out_failed visible`)
      }
      if (Object.keys(this.items_checked_out_successfully).length) {
        visible_columns++;
        console.log(`column_width():> this.items_checked_out_successfully visible`)
      }
      if (this.rfid_tags_present_filtered) {
        visible_columns++;
        console.log(`column_width():> this.rfid_tags_present visible`)
      }
      return (12 / visible_columns);
    }
  },
  methods: {
    user_login_failed: function (event) {
      this.$data.user = {};
      this.$emit('exception', event)
      //this.$emit('stop_checking_out');
    },
    user_login_success: function (event) {
      this.$data.user = event;
      this.start_transactions();
    },
    abort_user_login: function () {
      console.log("abort_user_login in CheckOut");
      lainuri_ws.dispatch_event(new LEUserLoginAbort('client', 'server'));
      this.stop_checking_out();
    },
    start_or_continue_transaction: function (tag) {
      console.log(`[${this.$options.name}]:> start_or_continue_transaction():> tag='${tag}'`)
      if (!tag.item_barcode) return;
      let item_bib = this.$data.transactions[tag.item_barcode]
      if (!item_bib) {
        console.log(`[${this.$options.name}]:> item_barcode='${tag.item_barcode}', starting check-out transaction`)
        this.$data.transactions[tag.item_barcode] = tag
        this.check_out_item(tag);
      }
      else {
        console.log(`[${this.$options.name}]:> item_barcode='${tag.item_barcode}', resuming check-out transaction`)
        if (tag.tag_type === 'rfid') {
          item_bib.tag_type = tag.tag_type; // The same item can be identified via barcode reader or the rfid reader. RFID is the dominant detection method and if rfid is used, the transaction has more steps.
        }
        if (item_bib.status_check_out === Status.NOT_SET || ! [Status.ERROR, Status.SUCCESS, Status.PENDING].includes(item_bib.status_check_out)) {
          console.log(`[${this.$options.name}]:> item_barcode='${item_bib.item_barcode}' status_check_out='${item_bib.status_check_out}', resuming check-out transaction - do check-out`)
          this.check_out_item(item_bib);
        }
        else if (tag.tag_type === 'rfid' && item_bib.status_set_tag_alarm === Status.NOT_SET || ! [Status.SUCCESS, Status.PENDING].includes(item_bib.status_set_tag_alarm)) {
          console.log(`[${this.$options.name}]:> item_barcode='${item_bib.item_barcode}' set_rfid_tag_alarm='${item_bib.status_set_tag_alarm}', resuming check-out transaction - set rfid tag security status`)
          this.set_rfid_tag_alarm(item_bib)
        }
      }
    },
    stop_checking_out: function () {
      console.log(`[${this.$options.name}]:> Stopped checking out`);
      this.$data.user = {};
      this.$emit('stop_checking_out');
    },
    stop_checkin_out_and_get_receipt: function () {
      console.log(`[${this.$options.name}]:> Stopping checking out and getting a receipt`);
      this.print_receipt();
      //this.stop_checking_out(); // The kill signal is given when the receipt printing confirmation is received from the server
    },
    start_transactions: function (event) {
      console.log(`[${this.$options.name}]:> Started transactions. Items present '${this.rfid_tags_present.length}'`);
      for (let i in this.rfid_tags_present) {
        this.start_or_continue_transaction(this.rfid_tags_present[i]);
      }
    },
    check_out_item: function (item_bib, delay) {
      console.log(`[${this.$options.name}]:> Checking out item '${item_bib.item_barcode}'`);
      if (! [Status.PENDING, Status.SUCCESS].includes(item_bib.status_check_out)) {
        ItemBib.prototype.set_status_check_out.call(item_bib, Status.PENDING)
        lainuri_ws.dispatch_event(new LECheckOut(item_bib.item_barcode, this.$data.user.user_barcode, item_bib.tag_type, 'client', 'server'))
      }
      else {
        console.error(`[${this.$options.name}]:> Checking out item '${item_bib.item_barcode}', but it is already being checked out?`);
      }
    },
    check_out_complete: function (event) {
      let item_bib = this.transactions[event.item_barcode]
      if (!item_bib) throw new Error(`Couldn't find a transaction regarding tag item_barcode='${event.item_barcode}'`);

      ItemBib.prototype.set_status_check_out.call(item_bib, event.status, event.states)

      if (item_bib.status_check_out === Status.SUCCESS) {
        this.items_checked_out_successfully[item_bib.item_barcode] = item_bib;
        delete this.items_checked_out_failed[item_bib.item_barcode]
      }
      else {
        this.items_checked_out_failed[item_bib.item_barcode] = item_bib;
        delete this.items_checked_out_successfully[item_bib.item_barcode]
      }

      if (Object.keys(item_bib.states_check_out).length) {
        this.overlay_notifications.push(item_bib);
      }

      if (item_bib.status_check_out === Status.SUCCESS) {
        if (item_bib.tag_type === 'rfid' && item_bib.status_set_tag_alarm === Status.NOT_SET) {
          this.set_rfid_tag_alarm(item_bib)
        }
      }
    },
    set_rfid_tag_alarm: function (item_bib) {
      console.log(`[${this.$options.name}]:> set_rfid_tag_alarm. item_barcode='${item_bib.item_barcode}'`);
      if (! [Status.PENDING, Status.SUCCESS].includes(item_bib.status_set_tag_alarm)) {
        ItemBib.prototype.set_status_set_tag_alarm.call(item_bib, Status.PENDING)
        lainuri_ws.dispatch_event(new LESetTagAlarm(item_bib.item_barcode, false, 'client', 'server'))
      }
      else {
        console.error(`[${this.$options.name}]:> set_rfid_tag_alarm. item_barcode '${item_bib.item_barcode}', but it is already being set?`);
      }
    },
    set_rfid_tag_alarm_complete: function (event) {
      let item_bib = this.transactions[event.item_barcode]
      if (!item_bib) throw new Error(`Couldn't find a transaction regarding tag item_barcode='${event.item_barcode}'`);

      ItemBib.prototype.set_status_set_tag_alarm.call(item_bib, event.status, event.states)
      if (event.status !== Status.SUCCESS) {
        this.overlay_notifications.push(item_bib);
      }
    },
    print_receipt: function () {
      console.log("Printing receipt");
      this.$data.receipt_printing = true;
      lainuri_ws.dispatch_event(
        new LEPrintRequest(
          'check-out',
          Object.values(this.$data.items_checked_out_successfully),
          this.$data.user.user_barcode,
        ),
      );
    },
    print_receipt_complete: function (event) {
      this.$data.receipt_printing = false;
      if (event.status !== Status.SUCCESS) {
        this.$emit('exception', event.status.exception);
      }
      this.stop_checking_out();
    },
    close_notification: function () {
      console.log("Closing notification");
      this.$data.overlay_notifications.shift();
    },
  },
  data: () => ({
    // Include imports
    Status: Status,

    receipt_printing: false,
    transactions: {}, // key is item_barcode
    user: Object,
    overlay_notifications: [],

    items_checked_out_successfully: {},
    items_checked_out_failed: {},

    /*items_checked_out_successfully: [
      {
        item_barcode: '167N00000123',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        status: 'success',
      },
    ],
    items_checked_out_failed: [
      {
        item_barcode: '167N00000001',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
        status: 'error',
        exception: 'Not available for anything',
      },
      {
        item_barcode: '167N00000111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        status: 'error',
        exception: 'Not available for anything',
      },
      {
        item_barcode: '167N00000321',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
        status: 'error',
        exception: 'Not available for anything',
      },
      {
        item_barcode: '167N00333111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        status: 'error',
        exception: 'Not available for anything',
      },
      {
        item_barcode: '167N00333001',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
        status: 'error',
      },
      {
        item_barcode: '167N00223111',
        book_cover_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Dummies for Grenades',
        author: 'Olli-Antti Kivilahti',
        status: 'error',
      },],*/
  }),
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
