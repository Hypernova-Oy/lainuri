<template>
  <v-container>
    <v-layout
      text-center
      wrap
    >
      <v-flex xs12>
        <v-img
          :src="require('../assets/logo.svg')"
          class="my-3"
          contain
          height="200"
        ></v-img>
      </v-flex>

      <v-container fluid>
        <v-row dense>
          <ItemCard v-for="tag in rfid_tags_present" v-bind:key="tag.barcode" :item_bib="tag"/>
        </v-row>
      </v-container>
    </v-layout>
  </v-container>
</template>

<script>
import ItemCard from '../components/ItemCard.vue'
import {start_ws, lainuri_set_vue, lainuri_ws, send_user_logging_in, abort_user_login} from '../lainuri'
import {LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed} from '../lainuri_events'


export default {
  name: 'Main',
  components: {
    ItemCard,
  },
  created: function () {
    this.$data.barcode_read = 'HASDHASHDAHSD';

    lainuri_set_vue(this);
    start_ws();

  },
  // define methods under the `methods` object
  methods: {
    enter_checkout_mode: function () {
      this.app_mode = 'mode_checkout';
      console.log("Entering 'mode_checkout'");
      this.barcode_read = '1234';
      send_user_logging_in();
    },
    enter_checkin_mode: function () {
      this.app_mode = 'mode_checkin';
      console.log("Entering 'mode_checkin'");
      this.barcode_read = '4321';
    },
    abort_user_login: function () {
      this.app_mode = 'mode_main_menu';
      abort_user_login();
    },
  },
  data: () => ({
    activeBtn: 1,
    name: 'Vue.js',
    app_mode: 'mode_main_menu',
    user: {},
    barcode_read: '',
    rfid_tags_present: [],
    cards: [
      { title: 'Pre-fab homes', src: 'https://cdn.vuetifyjs.com/images/cards/house.jpg', flex: 12 },
      { title: 'Favorite road trips', src: 'https://cdn.vuetifyjs.com/images/cards/road.jpg', flex: 6 },
      { title: 'Best airlines', src: 'https://cdn.vuetifyjs.com/images/cards/plane.jpg', flex: 6 },
    ],
    ecosystem: [
      {
        text: 'vuetify-loader',
        href: 'https://github.com/vuetifyjs/vuetify-loader',
      },
      {
        text: 'github',
        href: 'https://github.com/vuetifyjs/vuetify',
      },
      {
        text: 'awesome-vuetify',
        href: 'https://github.com/vuetifyjs/awesome-vuetify',
      },
    ],
    importantLinks: [
      {
        text: 'Documentation',
        href: 'https://vuetifyjs.com',
      },
      {
        text: 'Chat',
        href: 'https://community.vuetifyjs.com',
      },
      {
        text: 'Made with Vuetify',
        href: 'https://madewithvuejs.com/vuetify',
      },
      {
        text: 'Twitter',
        href: 'https://twitter.com/vuetifyjs',
      },
      {
        text: 'Articles',
        href: 'https://medium.com/vuetify',
      },
    ],
    whatsNext: [
      {
        text: 'Explore components',
        href: 'https://vuetifyjs.com/components/api-explorer',
      },
      {
        text: 'Select a layout',
        href: 'https://vuetifyjs.com/layout/pre-defined',
      },
      {
        text: 'Frequently Asked Questions',
        href: 'https://vuetifyjs.com/getting-started/frequently-asked-questions',
      },
    ],
  }),
};
</script>
