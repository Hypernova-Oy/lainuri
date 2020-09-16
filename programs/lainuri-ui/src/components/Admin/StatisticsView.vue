<template>
  <v-card class="statistics-view">
    <div>Checkouts: {{sum_checkouts}} Checkins: {{sum_checkins}}</div>
    <HistogramSlider :key="histogram_data.data[0]"
      style="margin: auto; padding-bottom: 10px;"
      :bar-height="500"
      :bar-gap="5"
      :bar-width="10"
      :bar-radius="4"
      :drag-interval="true"
      :grid-num="10"
      :line-height="10"
      :width="950"
      :data="histogram_data.data"
      :colors="['#4facfe', '#00f2fe']"
      :prettify="prettify_histogram"
      v-on:finish="update_slider_from_to"
      v-on:update="update_slider_from_to"
    />
    <v-card-actions>
      <v-btn
        id="export_statistics_as_csv"
        v-on:click="export_statistics_as_csv"
        x-large color="primary"
      >
        <v-icon>mdi-download</v-icon>
        Export as .csv
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import {get_logger} from '../../logger'
let log = get_logger('Admin/StatisticsView.vue');

import {lainuri_ws} from '../../lainuri'
import {Status, LETransactionHistoryRequest, LETransactionHistoryResponse} from '../../lainuri_events.js'

import * as Timeout from '../../timeout_poller'

let cached_transactions;
export default {
  name: 'StatisticsView',
  created: function () {
    lainuri_ws.attach_event_listener(LETransactionHistoryResponse, this, function(event) {
      log.info(`[StatisticsView.vue]:> Event 'LETransactionHistoryResponse' received.`);
      if (event.status === Status.SUCCESS) {
        cached_transactions = event.transactions;
        console.log(event);
        this.$set(this.$data.histogram_data, 'data', event.transactions.map(x => {
            return x.transaction_date*1000;
          })
        )
        this.$data.slider_from = this.$data.histogram_data.data[0]
        this.$data.slider_to = this.$data.histogram_data.data[this.$data.histogram_data.data.length-1]
        this.count_transactions();
      }
      else {
        this.$emit('exception', event);
      }
    });
  },
  mounted: function () {
    lainuri_ws.dispatch_when_ready(new LETransactionHistoryRequest(0, Date.now()));
  },
  beforeDestroy: function () {
    Timeout.terminate('CountTransactionsLazy');
    lainuri_ws.flush_listeners_for_component(this, this.$options.name);
  },
  data: () => ({
    slider_from: 0,
    slider_to: 0,
    sum_checkins: 0,
    sum_checkouts: 0,
    histogram_data: {
      data: [],
    },
  }),
  computed: {
  },
  methods: {
    update_slider_from_to: function (event) {
      this.$data.slider_from = event.from;
      this.$data.slider_to   = event.to;
      this.maybe_count_transactions();
    },
    prettify_histogram: function (datapoint) {
      let d = new Date();
      d.setTime(datapoint);
      return d.toLocaleString(this.$appConfig.i18n.default_locale);
    },
    export_statistics_as_csv: function () {
      let from_d = new Date();
      let from_s = (from_d.setTime(this.$data.slider_from)) / 1000;
      let from_ymd = from_d.toISOString().substr(0,10).replace(/-/g,'');
      let to_d = new Date();
      let to_s = (to_d.setTime(this.$data.slider_to)) / 1000;
      let to_ymd = to_d.toISOString().substr(0,10).replace(/-/g,'');
      let slice = ["transaction_date,transaction_type,borrower_barcode,item_barcode"];
      slice = this._gather_transactions(slice, this.format_csv_row)
      this.download(`lainuri-statistics-${from_ymd}-${to_ymd}.csv`, slice.join("\n"));
    },
    format_csv_row: function (t) {
      let pretty_date = new Date();
      pretty_date.setTime(t.transaction_date * 1000);
      return `"${pretty_date.toISOString().substr(0,19)}","${t.transaction_type.replace(/"/g,'"')}","${(t.borrower_barcode || '').replace(/"/g,'"')}","${t.item_barcode.replace(/"/g,'"')}"`;
    },
    count_transactions: function () {
      let sum_checkouts = 0;
      let sum_checkins = 0;
      this._gather_transactions([],function (t) {
        t.transaction_type === "checkin" ? sum_checkins++ : sum_checkouts++;
      });
      this.$data.sum_checkins = sum_checkins;
      this.$data.sum_checkouts = sum_checkouts;
    },
    _gather_transactions: function (list, formatter) {
      let from_s = (new Date().setTime(this.$data.slider_from)) / 1000;
      let to_s = (new Date().setTime(this.$data.slider_to)) / 1000;
      if (!list) list = [];
      for (let t of cached_transactions) {
        if (t.transaction_date >= from_s && t.transaction_date <= to_s) {
          list.push((formatter) ? formatter(t) : t);
        }
      }
      return list;
    },
    download: function (filename, text) {
      //Thanks https://ourcodeworld.com/articles/read/189/how-to-create-a-file-and-generate-a-download-with-javascript-in-the-browser-without-a-server
      let element = document.createElement('a');
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
      element.setAttribute('download', filename);
      element.style.display = 'none';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    },
    maybe_count_transactions: function () {
      Timeout.terminate('CountTransactionsLazy')
      Timeout.start('CountTransactionsLazy', () => {
        this.count_transactions();
      }, 1);
    },
  }
}
</script>

<style>
#export_statistics_as_csv {
  margin-left: auto;
}
</style>
