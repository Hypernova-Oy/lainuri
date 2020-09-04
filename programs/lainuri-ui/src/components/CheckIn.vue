<template>
  <v-container centered>
    <v-card raised class="subspace-navigation">
      <v-row>
        <v-col>
          <v-card-title>{{t('CheckIn/Place_items_on_the_reader_and_read_barcodes')}}</v-card-title>
        </v-col>
        <v-col>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              v-on:click="stop_checking_in"
              x-large color="secondary"
            >
              {{t('CheckIn/Finish')}}
            </v-btn>
            <v-btn v-if="$appConfig.devices['thermal-printer'].enabled && Object.keys(items_checked_in_successfully).length"
              v-on:click="stop_checkin_in_and_get_receipt"
              x-large color="secondary"
            >
              {{t('CheckIn/Finish+Receipt')}}
            </v-btn>
          </v-card-actions>
        </v-col>
      </v-row>
    </v-card>

    <v-row dense>
      <v-col v-if="Object.keys(items_checked_in_successfully).length"
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
            <v-toolbar-title>{{t('CheckIn/Your_Check_ins')}}</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-app-bar>

          <v-container class="item_scrollview">
            <v-row dense>
              <v-col
                v-for="(item_bib) in items_checked_in_successfully"
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
            <v-toolbar-title>{{t('CheckIn/In_Queue')}}</v-toolbar-title>
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

      <v-col v-if="Object.keys(items_checked_in_failed).length"
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
            <v-toolbar-title>{{t('CheckIn/Errors')}}</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-app-bar>

          <v-container class="item_scrollview">
            <v-row dense>
              <v-col
                v-for="(item_bib) in items_checked_in_failed"
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
    <v-overlay v-if="overlay_notifications.length" opacity="1">
      <transition name="fade" mode="out-in" appear>
        <OverlayNotification :key="overlay_notifications[0].item_barcode"
          :item_bib="overlay_notifications[0]"
          :mode="'checkin'"
          v-on:close_notification="close_notification"
        />
      </transition>
    </v-overlay>
  </v-container>
</template>

<script>
import {get_logger} from '../logger'
let log = get_logger('CheckIn.vue');

import ItemCard from '../components/ItemCard.vue'
import OverlayNotification from '../components/OverlayNotification.vue'
import PrintNotification from '../components/PrintNotification.vue'

import {find_tag_by_key} from '../helpers'
import {ItemBib} from '../item_bib'
import {lainuri_ws} from '../lainuri'
import {Status, LERFIDTagsNew, LECheckIn, LECheckInComplete, LEBarcodeRead, LEPrintRequest, LEPrintResponse, LESetTagAlarm, LESetTagAlarmComplete} from '../lainuri_events'
import * as Timeout from '../timeout_poller'


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
    Timeout.start('SessionTimeout', () => {
      this.$emit('exception', {type: "SessionTimeout"});
      this.stop_checking_in()
    }, this.$appConfig.ui.session_inactivity_timeout_s);

    lainuri_ws.attach_event_listener(LECheckInComplete, this, function(event) {
      log.info(`Event 'LECheckInComplete' for barcode='${event.item_barcode}'`); Timeout.prod('SessionTimeout');
      this.check_in_complete(event);
    });
    lainuri_ws.attach_event_listener(LEBarcodeRead, this, function(event) {
      log.info(`Event 'LEBarcodeRead' for barcode='${event.barcode}'`); Timeout.prod('SessionTimeout');
      this.start_or_continue_transaction(new ItemBib(event.tag))
    });
    lainuri_ws.attach_event_listener(LERFIDTagsNew, this, function(event) {
      log.info(`Event 'LERFIDTagsNew' triggered. New RFID tags:`, event.tags_new); Timeout.prod('SessionTimeout');
      for (let item_bib of event.tags_new) {
        let tags_present_item_bib_and_i = find_tag_by_key(this.rfid_tags_present, 'item_barcode', item_bib.item_barcode)
        if (! tags_present_item_bib_and_i) {
          log.fatal(`[CheckIn.vue]:> Event 'LERFIDTagsNew':> New item '${item_bib.item_barcode}' detected, but it is not in the this.$props.rfid_tags_present -list (length='${this.rfid_tags_present.length}') Main listener for new RFID tags should update the prop.`);
          throw new Error(`[CheckIn.vue]:> Event 'LERFIDTagsNew':> New item '${item_bib.item_barcode}' detected, but it is not in the this.$props.rfid_tags_present -list (length='${this.rfid_tags_present.length}') Main listener for new RFID tags should update the prop.`);
        }
        this.start_or_continue_transaction(tags_present_item_bib_and_i[0]);
      }
    });
    lainuri_ws.attach_event_listener(LESetTagAlarmComplete, this, function(event) {
      log.info(`Event 'LESetTagAlarmComplete' for item_barcode='${event.item_barcode}'`); Timeout.prod('SessionTimeout');
      this.set_rfid_tag_alarm_complete(event);
    });
    lainuri_ws.attach_event_listener(LEPrintResponse, this, function(event) {
      log.info(`Event 'LEPrintResponse'`); Timeout.prod('SessionTimeout');
      if (this.receipt_printing) {this.print_receipt_complete(event);}
      else {log.error(`Received event 'LEPrintResponse' but not printing a receipt. User race condition maybe?`)}
    });
  },
  mounted: function () {
    this.start_transactions();
  },
  beforeDestroy: function () {
    Timeout.terminate('*');
    lainuri_ws.flush_listeners_for_component(this, this.$options.name);
    this.items_checked_in_failed = {}
    this.items_checked_in_successfully = {}
  },
  computed: {
    transactions_queue: function () {
      let filtered_statuses = [Status.PENDING, Status.NOT_SET]

      let queue = {}
      for (let item_bib of this.rfid_tags_present) {
        // For existing transactions use the existing object instance and it's statuses, for example if the barcode read was upgraded to rfid.
        let item_bib_already_in_transaction = this.transactions[item_bib.item_barcode]
        if (item_bib_already_in_transaction) {
          if (filtered_statuses.includes(item_bib_already_in_transaction.status_check_in)) {
            queue[item_bib_already_in_transaction.item_barcode] = item_bib_already_in_transaction
          }
        }
        else {
          if (filtered_statuses.includes(item_bib.status_check_in)) {
            queue[item_bib.item_barcode] = item_bib
          }
        }
      }

      for (let item_bib of Object.values(this.transactions)) {
        if (!(queue[item_bib.item_barcode]) && filtered_statuses.includes(item_bib.status_check_in)) {
          queue[item_bib.item_barcode] = item_bib
        }
      }
      return queue
    },
    column_width: function () {
      if (! this.$appConfig.ui.use_bookcovers) return 12;

      let visible_columns = 0;
      if (Object.keys(this.items_checked_in_failed).length) {
        visible_columns++;
        log.trace('column_width():> this.items_checked_in_failed visible')
      }
      if (Object.keys(this.items_checked_in_successfully).length) {
        visible_columns++;
        log.trace('column_width():> this.items_checked_in_successfully visible')
      }
      if (Object.keys(this.transactions_queue).length) {
        visible_columns++;
        log.trace('column_width():> this.transactions_queue visible')
      }
      return (12 / visible_columns);
    }
  },
  methods: {
    start_or_continue_transaction: function (tag) {
      log.info('start_or_continue_transaction():> tag=', tag);
      if (!tag.item_barcode) {
        //this.check_in_failed(tag, {exception: {type: 'NoItemIdentifier'}})
        //this.$emit('exception', { type: 'NoItemIdentifier'})
        return;
      }
      let item_bib = this.$data.transactions[tag.item_barcode]
      if (!item_bib) {
        log.info(`start_or_continue_transaction():> item_barcode='${tag.item_barcode}', starting check-in transaction`)
        this.$set(this.$data.transactions, tag.item_barcode, tag)
        this.check_in_item(tag);
      }
      else {
        log.info(`start_or_continue_transaction():> item_barcode='${tag.item_barcode}', resuming check-in transaction`)
        if (item_bib.tag_type === 'barcode' && tag.tag_type === 'rfid') {
          // The same item can be identified via barcode reader or the rfid reader. RFID is the dominant detection method and if rfid is used, the transaction has more steps.
          // Here we upgrade an existing transaction to 'rfid'
          item_bib.tag_type = tag.tag_type;
          let new_rfid_item_bib_and_i = find_tag_by_key(this.rfid_tags_present, 'item_barcode', item_bib.item_barcode)
          this.rfid_tags_present[ new_rfid_item_bib_and_i[1] ] = item_bib;
        }
        if (item_bib.status_check_in === Status.NOT_SET || ! [Status.ERROR, Status.SUCCESS, Status.PENDING].includes(item_bib.status_check_in)) {
          log.info(`start_or_continue_transaction():> item_barcode='${item_bib.item_barcode}' status_check_in='${item_bib.status_check_in}', resuming check-in transaction - do check-in`)
          this.check_in_item(item_bib);
        }
        else if (item_bib.tag_type === 'rfid' &&
                 item_bib.status_check_in === Status.SUCCESS &&
                 (item_bib.status_set_tag_alarm === Status.NOT_SET || ! [Status.SUCCESS, Status.PENDING].includes(item_bib.status_set_tag_alarm))) {
          log.info(`start_or_continue_transaction():> item_barcode='${item_bib.item_barcode}' set_rfid_tag_alarm='${item_bib.status_set_tag_alarm}', resuming check-in transaction - set rfid tag security status`)
          this.set_rfid_tag_alarm(item_bib)
        }
        else {
          log.debug(`Hiding tag item_barcode='${tag.item_barcode}' because it has been completely handled`)
          tag.status_check_in = Status.ERROR; // Hide the tag from the pending queue if there is nothing left to do.
        }
      }
    },
    stop_checking_in: function () {
      log.info(`Stopped checking in`);
      this.$data.user = {};
      this.$emit('stop_checking_in');
    },
    stop_checkin_in_and_get_receipt: function () {
      log.info(`Stopping checking in and getting a receipt`);
      this.print_receipt();
      //this.stop_checking_in(); // The kill signal is given when the receipt printing confirmation is received from the server
    },
    start_transactions: function (event) {
      log.info(`Started transactions. Items present '${this.rfid_tags_present.length}'`);
      for (let i in this.rfid_tags_present) {
        this.start_or_continue_transaction(this.rfid_tags_present[i]);
      }
    },
    check_in_item: function (item_bib, delay) {
      log.info(`Checking in item '${item_bib.item_barcode}'`);
      if (! [Status.PENDING, Status.SUCCESS].includes(item_bib.status_check_in)) {
        ItemBib.prototype.set_status_check_in.call(item_bib, Status.PENDING)
        lainuri_ws.dispatch_event(new LECheckIn(item_bib.item_barcode, item_bib.tag_type, 'client', 'server'))
      }
      else {
        log.error(`Checking in item '${item_bib.item_barcode}', but it is already being checked in?`);
      }
    },
    check_in_complete: function (event) {
      let item_bib = this.transactions[event.item_barcode]
      if (!item_bib) {
        log.fatal(`check_in_complete():> Couldn't find a transaction regarding tag item_barcode='${event.item_barcode}'`)
        throw new Error(`check_in_complete():> Couldn't find a transaction regarding tag item_barcode='${event.item_barcode}'`);
      }
      this.$set(item_bib, 'sort_to', event.sort_to)

      if (event.status === Status.SUCCESS) {
        this.check_in_succeeded(item_bib, event.states);
        if (item_bib.tag_type === "barcode") {
          this.show_overlay_notification(item_bib);  //The transaction ends here for a barcode-Item.
        }
      }
      else {
        this.check_in_failed(item_bib, event.states);
        this.show_overlay_notification(item_bib);
      }
    },
    check_in_failed: function (item_bib, states) {
      ItemBib.prototype.set_status_check_in.call(item_bib, Status.ERROR, states)
      this.items_checked_in_failed[item_bib.item_barcode] = item_bib;
      delete this.items_checked_in_successfully[item_bib.item_barcode]
    },
    check_in_succeeded: function (item_bib, states) {
      ItemBib.prototype.set_status_check_in.call(item_bib, Status.SUCCESS, states)
      this.items_checked_in_successfully[item_bib.item_barcode] = item_bib;
      delete this.items_checked_in_failed[item_bib.item_barcode]

      if (item_bib.tag_type === 'rfid' && item_bib.status_set_tag_alarm === Status.NOT_SET) {
        this.set_rfid_tag_alarm(item_bib)
      }
    },
    set_rfid_tag_alarm: function (item_bib) {
      log.info(`set_rfid_tag_alarm():> item_barcode='${item_bib.item_barcode}'`);
      if (! [Status.PENDING, Status.SUCCESS].includes(item_bib.status_set_tag_alarm)) {
        ItemBib.prototype.set_status_set_tag_alarm.call(item_bib, Status.PENDING)
        lainuri_ws.dispatch_event(new LESetTagAlarm(item_bib.item_barcode, true, 'client', 'server'))
      }
      else {
        log.error(`set_rfid_tag_alarm():> item_barcode '${item_bib.item_barcode}', but it is already being set?`);
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
      if (this.$appConfig.ui.always_display_check_in_out_notification ||
          Object.keys(item_bib.states).length) {
        this.overlay_notifications.push(item_bib);

        if (item_bib._overlay_notificated) log.warn(`show_overlay_notification() item_barcode '${item_bib.item_barcode}', duplicate overlay notification!`);
        item_bib._overlay_notificated = true; // a regression trap
      }
    },
    print_receipt: function () {
      log.info(`Printing receipt`);
      this.$data.receipt_printing = true;
      lainuri_ws.dispatch_event(
        new LEPrintRequest(
          'check-in',
          Object.values(this.$data.items_checked_in_successfully),
          ''
        ),
      );
    },
    print_receipt_complete: function (event) {
      this.$data.receipt_printing = false;
      if (event.status !== Status.SUCCESS) {
        this.$emit('exception', event.status.exception);
      }
      this.stop_checking_in();
    },
    close_notification: function () {
      log.debug("Closing notification");
      Timeout.prod('SessionTimeout');
      this.$data.overlay_notifications.shift();
    },
  },
  data: () => ({
    // Include imports
    Status: Status,

    receipt_printing: false,
    transactions: {}, // key is item_barcode
    overlay_notifications: [],
    items_checked_in_successfully: {},
    items_checked_in_failed: {},
  }),
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.subspace-navigation .v-card__title, .subspace-navigation button.v-btn {
  font-size: 1.6em;
  font-weight: 900;
  height: 100%;
}
.subspace-navigation .v-card__actions {
  height: 100%;
}
.v-toolbar__title {
  font-weight: 900;
  font-size: 1.6rem;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
