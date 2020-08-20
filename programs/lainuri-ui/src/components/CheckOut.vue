<template>
  <v-container centered>
    <v-card raised class="subspace-navigation">
      <v-row>
        <v-col>
          <v-card-title v-if="! is_user_logged_in">{{t('CheckOut/Read_library_card')}}</v-card-title>
          <v-card-title v-if="is_user_logged_in">
            {{t('CheckOut/Hi_user!', {user: user.firstname})}}<br/>
            {{t('CheckOut/Place_items_on_the_reader_and_read_barcodes')}}
          </v-card-title>
        </v-col>
        <v-col>
          <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn
              v-on:click="stop_checking_out"
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
              {{t('CheckOut/Finish')}}
            </v-btn>
            <v-btn
              v-on:click="stop_checkin_out_and_get_receipt"
              v-if="is_user_logged_in && Object.keys(items_checked_out_successfully).length"
              x-large color="secondary"
            >
              {{t('CheckOut/Finish+Receipt')}}
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

      <v-col v-if="Object.keys(transactions_queue).length"
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
                v-for="(item_bib) in transactions_queue"
                :key="item_bib.item_barcode || item_bib.serial_number"
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
    <v-overlay :value="overlay_notifications.length" opacity="1">
      <OverlayNotification
        :item_bib="overlay_notifications[0]"
        :mode="'checkout'"
        v-on:close_notification="close_notification"
      />
    </v-overlay>

  </v-container>
</template>

<script>
import {get_logger} from '../logger'
let log = get_logger('CheckOut.vue');

import ItemCard from '../components/ItemCard.vue'
import OverlayNotification from '../components/OverlayNotification.vue'
import PrintNotification from '../components/PrintNotification.vue'

import {find_tag_by_key} from '../helpers'
import {ItemBib} from '../item_bib'
import {lainuri_ws, send_user_logging_in} from '../lainuri'
import {Status, LEUserLoginComplete, LEUserLoggingIn, LEUserLoginAbort, LERFIDTagsNew, LECheckOut, LECheckOutComplete, LEBarcodeRead, LEPrintRequest, LEPrintResponse, LESetTagAlarm, LESetTagAlarmComplete} from '../lainuri_events'
import * as Timeout from '../timeout_poller'


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
    Timeout.start(() => {
      this.$emit('exception', {type: "SessionTimeout"});
      this.stop_checking_out()
    }, this.$appConfig.ui.session_inactivity_timeout_s);

    lainuri_ws.attach_event_listener(LEUserLoginComplete, this, (event) => {
      log.info(`Received event 'LEUserLoginComplete'`); Timeout.prod();
      if (event.status === Status.SUCCESS) {
        if (! this.is_user_logged_in) {
          this.user_login_success(event);
        }
        else {
          log.error(`User '${this.$data.user.user_barcode}' already logged in? Login attempt from user '${event.user_barcode}'`);
        }
      }
      else {
        this.user_login_failed(event);
      }
    });
    lainuri_ws.attach_event_listener(LECheckOutComplete, this, function(event) {
      log.info(`Received event 'LECheckOutComplete' for barcode='${event.item_barcode}'`); Timeout.prod();
      this.check_out_complete(event);
    });
    lainuri_ws.attach_event_listener(LEBarcodeRead, this, function(event) {
      log.info(`Event 'LEBarcodeRead' for barcode='${event.barcode}'`); Timeout.prod();
      if (this.is_user_logged_in) {
        this.start_or_continue_transaction(new ItemBib(event.tag))
      }
      else {
        log.error(`Received event 'LEBarcodeRead' for barcode='${event.barcode}', but no user logged in?`);
      }
    });
    lainuri_ws.attach_event_listener(LERFIDTagsNew, this, function(event) {
      log.info(`Event 'LERFIDTagsNew' triggered. New RFID tags:`, event.tags_new); Timeout.prod();
      if (this.is_user_logged_in) {
        for (let item_bib of event.tags_new) {
          let tags_present_item_bib_and_i = find_tag_by_key(this.rfid_tags_present, 'item_barcode', item_bib.item_barcode)
          if (! tags_present_item_bib_and_i) {
            throw new Error(`[${this.$options.name}]:> Event 'LERFIDTagsNew':> New item '${item_bib.item_barcode}' detected, but it is not in the this.$props.rfid_tags_present -list (length='${this.rfid_tags_present.length}') Main listener for new RFID tags should update the prop.`);
          }
          this.start_or_continue_transaction(tags_present_item_bib_and_i[0]);
        }
      }
      else {
        log.info(`Event 'LERFIDTagsNew' triggered. User not logged in yet.`);
      }
    });
    lainuri_ws.attach_event_listener(LESetTagAlarmComplete, this, function(event) {
      log.info(`Event 'LESetTagAlarmComplete' for item_barcode='${event.item_barcode}'`); Timeout.prod();
      this.set_rfid_tag_alarm_complete(event);
    });
    lainuri_ws.attach_event_listener(LEPrintResponse, this, function(event) {
      log.info(`Event 'LEPrintResponse'`); Timeout.prod();
      if (this.receipt_printing) {this.print_receipt_complete(event);}
      else {log.error(`Received event 'LEPrintResponse' but not printing a receipt. User race condition maybe?`)}
    });
  },
  beforeDestroy: function () {
    Timeout.terminate();
    lainuri_ws.flush_listeners_for_component(this, this.$options.name);
    this.items_checked_out_failed = {}
    this.items_checked_out_successfully = {}
  },
  computed: {
    is_user_logged_in: function () {
      return (this.$data.user.user_barcode) ? true : false;
    },
    transactions_queue: function () {
      let filtered_statuses = [Status.PENDING, Status.NOT_SET]

      let queue = {}
      for (let item_bib of this.rfid_tags_present) {
        // For existing transactions use the existing object instance and it's statuses, for example if the barcode read was upgraded to rfid.
        let item_bib_already_in_transaction = this.transactions[item_bib.item_barcode]
        if (item_bib_already_in_transaction) {
          if (filtered_statuses.includes(item_bib_already_in_transaction.status_check_out)) {
            queue[item_bib_already_in_transaction.item_barcode] = item_bib_already_in_transaction
          }
        }
        else {
          if (filtered_statuses.includes(item_bib.status_check_out)) {
            queue[item_bib.item_barcode] = item_bib
          }
        }
      }

      for (let item_bib of Object.values(this.transactions)) {
        if (!(queue[item_bib.item_barcode]) && filtered_statuses.includes(item_bib.status_check_out)) {
          queue[item_bib.item_barcode] = item_bib
        }
      }
      return queue
    },
    column_width: function () {
      let visible_columns = 0;
      if (Object.keys(this.items_checked_out_failed).length) {
        visible_columns++;
        log.trace('column_width():> this.items_checked_out_failed visible')
      }
      if (Object.keys(this.items_checked_out_successfully).length) {
        visible_columns++;
        log.trace('column_width():> this.items_checked_out_successfully visible')
      }
      if (Object.keys(this.transactions_queue).length) {
        visible_columns++;
        log.trace('column_width():> this.transactions_queue visible')
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
      log.info("abort_user_login in CheckOut");
      lainuri_ws.dispatch_event(new LEUserLoginAbort('client', 'server'));
    },
    start_or_continue_transaction: function (tag) {
      log.info('start_or_continue_transaction():> tag=', tag)
      if (!tag.item_barcode) {
        //this.check_in_failed(tag, {exception: {type: 'NoItemIdentifier'}})
        //this.$emit('exception', { type: 'NoItemIdentifier'})
        return;
      }
      let item_bib = this.$data.transactions[tag.item_barcode]
      if (!item_bib) {
        log.info(`start_or_continue_transaction():> item_barcode='${tag.item_barcode}', starting check-out transaction`)
        this.$set(this.$data.transactions, tag.item_barcode, tag)
        this.check_out_item(tag);
      }
      else {
        log.info(`start_or_continue_transaction():> item_barcode='${tag.item_barcode}', resuming check-out transaction`)
        if (item_bib.tag_type === 'barcode' && tag.tag_type === 'rfid') {
          // The same item can be identified via barcode reader or the rfid reader. RFID is the dominant detection method and if rfid is used, the transaction has more steps.
          // Here we upgrade an existing transaction to 'rfid'
          item_bib.tag_type = tag.tag_type;
          let new_rfid_item_bib_and_i = find_tag_by_key(this.rfid_tags_present, 'item_barcode', item_bib.item_barcode)
          this.rfid_tags_present[ new_rfid_item_bib_and_i[1] ] = item_bib;
        }
        if (item_bib.status_check_out === Status.NOT_SET || ! [Status.ERROR, Status.SUCCESS, Status.PENDING].includes(item_bib.status_check_out)) {
          log.info(`start_or_continue_transaction():> item_barcode='${item_bib.item_barcode}' status_check_out='${item_bib.status_check_out}', resuming check-out transaction - do check-out`)
          this.check_out_item(item_bib);
        }
        else if (item_bib.tag_type === 'rfid' &&
                 item_bib.status_check_out === Status.SUCCESS &&
                 (item_bib.status_set_tag_alarm === Status.NOT_SET || ! [Status.SUCCESS, Status.PENDING].includes(item_bib.status_set_tag_alarm))) {
          log.info(`start_or_continue_transaction():> item_barcode='${item_bib.item_barcode}' set_rfid_tag_alarm='${item_bib.status_set_tag_alarm}', resuming check-out transaction - set rfid tag security status`)
          this.set_rfid_tag_alarm(item_bib)
        }
        else {
          log.debug(`Hiding tag item_barcode='${tag.item_barcode}' because it has been completely handled`)
          tag.status_check_out = Status.ERROR; // Hide the tag from the pending queue if there is nothing left to do.
        }
      }
    },
    stop_checking_out: function () {
      log.info(`Stopped checking out`);
      if (!(this.$data.user) || Object.keys(this.$data.user).length == 0) this.abort_user_login();
      this.$data.user = {};
      this.$emit('stop_checking_out');
    },
    stop_checkin_out_and_get_receipt: function () {
      log.info(`Stopping checking out and getting a receipt`);
      this.print_receipt();
      //this.stop_checking_out(); // The kill signal is given when the receipt printing confirmation is received from the server
    },
    start_transactions: function (event) {
      log.info(`Started transactions. Items present '${this.rfid_tags_present.length}'`);
      for (let i in this.rfid_tags_present) {
        this.start_or_continue_transaction(this.rfid_tags_present[i]);
      }
    },
    check_out_item: function (item_bib, delay) {
      log.info(`Checking out item '${item_bib.item_barcode}'`);
      if (! [Status.PENDING, Status.SUCCESS].includes(item_bib.status_check_out)) {
        ItemBib.prototype.set_status_check_out.call(item_bib, Status.PENDING)
        lainuri_ws.dispatch_event(new LECheckOut(item_bib.item_barcode, this.$data.user.user_barcode, item_bib.tag_type, 'client', 'server'))
      }
      else {
        log.error(`Checking out item '${item_bib.item_barcode}', but it is already being checked out?`);
      }
    },
    check_out_complete: function (event) {
      let item_bib = this.transactions[event.item_barcode]
      if (!item_bib) {
        log.fatal(`check_in_complete():> Couldn't find a transaction regarding tag item_barcode='${event.item_barcode}'`)
        throw new Error(`check_in_complete():> Couldn't find a transaction regarding tag item_barcode='${event.item_barcode}'`);
      }

      if (event.status === Status.SUCCESS) {
        this.check_out_succeeded(item_bib, event.states);
        if (item_bib.tag_type === "barcode") {
          this.show_overlay_notification(item_bib);  //The transaction ends here for a barcode-Item.
        }
      }
      else {
        this.check_out_failed(item_bib, event.states);
        this.show_overlay_notification(item_bib);
      }
    },
    check_out_failed: function (item_bib, states) {
      ItemBib.prototype.set_status_check_out.call(item_bib, Status.ERROR, states)
      this.items_checked_out_failed[item_bib.item_barcode] = item_bib;
      delete this.items_checked_out_successfully[item_bib.item_barcode]
    },
    check_out_succeeded: function (item_bib, states) {
      ItemBib.prototype.set_status_check_out.call(item_bib, Status.SUCCESS, states)
      this.items_checked_out_successfully[item_bib.item_barcode] = item_bib;
      delete this.items_checked_out_failed[item_bib.item_barcode]

      if (item_bib.tag_type === 'rfid' && item_bib.status_set_tag_alarm === Status.NOT_SET) {
        this.set_rfid_tag_alarm(item_bib)
      }
    },
    set_rfid_tag_alarm: function (item_bib) {
      log.info(`set_rfid_tag_alarm. item_barcode='${item_bib.item_barcode}'`);
      if (! [Status.PENDING, Status.SUCCESS].includes(item_bib.status_set_tag_alarm)) {
        ItemBib.prototype.set_status_set_tag_alarm.call(item_bib, Status.PENDING)
        lainuri_ws.dispatch_event(new LESetTagAlarm(item_bib.item_barcode, false, 'client', 'server'))
      }
      else {
        log.error(`set_rfid_tag_alarm. item_barcode '${item_bib.item_barcode}', but it is already being set?`);
      }
    },
    set_rfid_tag_alarm_complete: function (event) {
      let item_bib = this.transactions[event.item_barcode]
      if (!item_bib) {
        log.fatal(`set_rfid_tag_alarm_complete():> Couldn't find a transaction regarding tag item_barcode='${event.item_barcode}'`)
        throw new Error(`set_rfid_tag_alarm_complete():> Couldn't find a transaction regarding tag item_barcode='${event.item_barcode}'`);
      }

      ItemBib.prototype.set_status_set_tag_alarm.call(item_bib, event.status, event.states)

      this.show_overlay_notification(item_bib); //The transaction ends here for a rfid-tag-Item.
    },
    show_overlay_notification: function (item_bib) {
      if (Object.keys(item_bib.states).length) {
        this.overlay_notifications.push(item_bib);

        if (item_bib._overlay_notificated) log.warn(`show_overlay_notification() item_barcode '${item_bib.item_barcode}', duplicate overlay notification!`);
        item_bib._overlay_notificated = true; // a regression trap
      }
    },
    print_receipt: function () {
      log.info("Printing receipt");
      this.$data.receipt_printing = true;
      lainuri_ws.dispatch_event(
        new LEPrintRequest(
          'check-out',
          Object.values(this.$data.items_checked_out_successfully),
          this.$data.user.user_barcode
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
      log.info("Closing notification");
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
  }),
}
</script>

<style scoped>
.subspace-navigation .v-card__title, .subspace-navigation button.v-btn {
  font-size: 1.5em;
  font-weight: 900;
}
.subspace-navigation .v-card__actions {
  height: 100%;
}
.v-toolbar__title {
  font-weight: 900;
  font-size: 1.5rem;
}
</style>
