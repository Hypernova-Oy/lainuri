<template>
    <v-card
      ripple
      raised
      v-bind:class="{
        error: item_bib.status === Status.ERROR,
        success: item_bib.status === Status.SUCCESS,
        pending: item_bib.status === Status.PENDING,
        'itemcard-layout-bookcover': $appConfig.ui.use_bookcovers === true,
        'itemcard-layout-rows': $appConfig.ui.use_bookcovers === false,
      }"
      class="itemcard"
      @click="overlay = !overlay"
    >
      <div class="iconosphere">
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
      </div>

      <v-img
        v-if="$appConfig.ui.use_bookcovers"
        :src="item_bib.book_cover_url || $appConfigGetImageOverload('bookcover-missing-placeholder')"
        contain
        height="50%"
        class="white--text align-end"
        gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
      ></v-img>
      <div class="itemcard-content">
        <v-card-text class="v-title-fix" v-text="item_bib.title || '...'"></v-card-text>
        <v-card-subtitle>
          <div>{{item_bib.author}}</div>
          <div>{{item_bib.edition}}</div>
          <div>{{item_bib.item_barcode}}</div>
        </v-card-subtitle>
      </div>
      <v-progress-circular
        v-if="$appConfig.ui.use_bookcovers === true && item_bib.status === Status.PENDING"
        class="progress"
        size="150"
        width="25"
        color="primary"
        indeterminate
      ></v-progress-circular>
      <v-progress-linear
        v-if="$appConfig.ui.use_bookcovers === false && item_bib.status === Status.PENDING"
        class="progress"
        indeterminate
      ></v-progress-linear>

      <v-overlay absolute :value="overlay"
        v-if="Object.keys(item_bib.states).length"
      >
        <v-card-text class="item-states">
          <ul>
            <li v-for="(i18n_key) in Object.keys(item_bib.states)"
                :key="i18n_key"
            >
              {{t(i18n_key)}}
            </li>
          </ul>
        </v-card-text>
      </v-overlay>
    </v-card>
</template>

<script>
import {ItemBib} from '../item_bib.js'
import {Status} from '../lainuri_events.js'

export default {
  name: 'ItemCard',
  components: {
  },
  props: {
    item_bib: ItemBib,
  },
  data: () => ({
    // Include imports
    Status: Status,

    overlay: false,
  }),
  created: function () {
    this.$data.overlay = this.$appConfig.ui.show_item_statuses // seed the initial value from the app config
  },
}
</script>

<style scoped>
.itemcard-layout-bookcover.itemcard {
  width: 240px;
/*  height: 350px;*/
}
.itemcard-layout-bookcover.itemcard .iconosphere {
  max-height: 24px;
}
.itemcard-layout-bookcover.itemcard .v-image {
  height: 170px;
  max-height: 170px;
}
.itemcard-layout-bookcover .itemcard-content {
  height: 156px;
  max-height: 156px;
  white-space: wrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.itemcard-layout-bookcover .itemcard-content .v-card__title {
  overflow: hidden;
}
.itemcard-layout-bookcover.itemcard .item-states {
  font-size: 1.4em;
  /*font-weight: bold;*/
}
.itemcard-layout-bookcover .progress {
  position: absolute;
  top: 20%;
  left: 20%;
}
.itemcard-layout-bookcover .v-title-fix {
  font-size: 1.24rem;
  overflow: hidden;
  padding-bottom: 0px;
}

.itemcard-layout-rows {
  width: 880px;
}
.itemcard-layout-rows .itemcard-content {
  display: flex;
}
.itemcard-layout-rows .v-card__text {
  width: initial;
  float: left;
  font-size: 1.4em;
}
.itemcard-layout-rows .v-card__subtitle {
  float: left;
  font-size: 1.2em;
}
.itemcard-layout-rows .v-card__subtitle div {
  float: left;
  margin: 0px 10px 0px 0px;
}
.itemcard-layout-rows .iconosphere {
  padding: 15px 16px 14px 0px;
  float: right;
}

</style>
