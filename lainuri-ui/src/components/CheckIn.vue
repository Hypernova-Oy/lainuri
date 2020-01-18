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
  </v-container>
</template>

<script>
import {start_ws, lainuri_set_vue, lainuri_ws, send_user_logging_in, abort_user_login} from '../lainuri'
import {LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed} from '../lainuri_events'

import ItemCard from '../components/ItemCard.vue'

let emited = 0
export default {
  name: 'CheckIn',
  components: {
    ItemCard,
  },
  props: {
    rfid_tags_present: Array,
  },
  methods: {
    stop_checking_in: function () {
      console.log("Stopped checking in");
      this.$emit('stop_checking_in');
    },
    stop_checkin_in_and_get_receipt: function () {
      console.log("Stopping checking in and getting a receipt");
      this.stop_checking_in();
    }
  },
  data: () => ({
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
