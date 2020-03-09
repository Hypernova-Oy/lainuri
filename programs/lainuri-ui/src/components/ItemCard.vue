<template>
    <v-card
      ripple
      raised
      v-bind:class="{
        error: item_bib.status === Status.ERROR,
        success: item_bib.status === Status.SUCCESS,
        pending: item_bib.status === Status.PENDING,
      }"
      class="itemcard"
      @click="overlay = !overlay"
    >
      <v-icon v-if="item_bib.tag_type === 'rfid'"                                         >mdi-access-point</v-icon>
      <v-icon v-else-if="item_bib.tag_type === 'barcode'"                                 >mdi-barcode</v-icon>
      <!-- Render transaction step status icons here -->
      <v-icon v-if="item_bib.status_check_in === Status.SUCCESS"       color="success darken-2"    >mdi-login</v-icon>
      <v-icon v-else-if="item_bib.status_check_in === Status.PENDING"  color="yellow darken-2"     >mdi-login</v-icon>
      <v-icon v-else-if="item_bib.status_check_in === Status.ERROR"    color="error darken-2"      >mdi-login</v-icon>
      <v-icon v-if="item_bib.status_check_out === Status.SUCCESS"      color="success darken-2"    >mdi-logout</v-icon>
      <v-icon v-else-if="item_bib.status_check_out === Status.PENDING" color="yellow darken-2"     >mdi-logout</v-icon>
      <v-icon v-else-if="item_bib.status_check_out === Status.ERROR"   color="error darken-2"      >mdi-logout</v-icon>
      <v-icon v-if="item_bib.status_set_tag_alarm === Status.SUCCESS"  color="success darken-2"    >mdi-alarm-light-outline</v-icon>
      <v-icon v-else-if="item_bib.status_set_tag_alarm === Status.PENDING" color="yellow darken-2" >mdi-alarm-light-outline</v-icon>
      <v-icon v-else-if="item_bib.status_set_tag_alarm === Status.ERROR" color="error darken-2"    >mdi-alarm-light-outline</v-icon>

      <v-img
        :src="item_bib.book_cover_url || 'image-placeholder.png'"
        contain
        height="50%"
        class="white--text align-end"
        gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
      >
        <v-progress-circular
          v-if="item_bib.status === Status.PENDING"
          class="progress"
          size="150"
          width="25"
          color="primary"
          indeterminate
        ></v-progress-circular>
      </v-img>
      <span class="itemcard-content">
        <v-card-title v-text="item_bib.title || '...'"></v-card-title>
        <v-card-subtitle><div>{{item_bib.author || 'x'}}</div><div>{{item_bib.edition || 'x'}}</div></v-card-subtitle>
        <v-card-text v-text="item_bib.item_barcode"></v-card-text>
      </span>
      <v-overlay absolute :value="overlay"
        v-if="exception_summary"
      >
        <v-card-text>
          {{exception_summary}}
        </v-card-text>
      </v-overlay>
    </v-card>
</template>

<script>

import {ItemBib} from '../item_bib.js'
import {Status} from '../lainuri_events.js'
import {translate_exception} from '../exception.js'

export default {
  name: 'CheckOut',
  props: {
    item_bib: ItemBib,
  },
  data: () => ({
    // Include imports
    Status: Status,

    overlay: true,
  }),
  created: function () {

  },
  computed: {
    exception_summary: function () {
      let e_str = '';
      if (this.item_bib.states_check_in) e_str += translate_exception(this.item_bib.states_check_in);
      if (this.item_bib.states_set_tag_alarm) e_str += translate_exception(this.item_bib.states_set_tag_alarm);
      return e_str;
    },
  },
}
</script>

<style scoped>
.itemcard {
  width: 240px;
  height: 350px;
}
.itemcard-content {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.itemcard-content .v-card__title {
  overflow: hidden;
}
.progress {
  position: absolute;
  top: 25%;
  left: 20%;
}
</style>
