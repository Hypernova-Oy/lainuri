<template>
  <v-card
    class="overflow-hidden"
  >

    <v-sheet
      id="scroll-area-1"
      class="overflow-y-auto"
      max-height="600"
    >
      <v-container v-if="bottom_bar_view === undefined" style="height: 60px;">

      </v-container>
      <v-container v-if="bottom_bar_view == 'debug'" style="height: 1500px;">
          DEBUG MODE ACTIVATED!
      </v-container>
      <v-container v-if="bottom_bar_view == 'config'" style="height: 1500px;">
          !ACTIVATED CONFIG MODE
      </v-container>
    </v-sheet>

    <v-bottom-navigation
      absolute
      horizontal
    >
      <v-btn @click="bottom_bar_view='debug'"
        text color="deep-purple accent-4"
      >
        <span>Recents</span>
        <v-icon>mdi-history</v-icon>
      </v-btn>

      <v-btn @click="bottom_bar_view=undefined"
        text color="deep-purple accent-4"
      >
        <span>Favorites</span>
        <v-icon>mdi-heart</v-icon>
      </v-btn>

      <v-btn @click="bottom_bar_view='config'"
        text color="deep-purple accent-4"
      >
        <span>Nearby</span>
        <v-icon>mdi-map-marker</v-icon>
      </v-btn>
    </v-bottom-navigation>
  </v-card>
</template>

<script>
import {start_ws, lainuri_set_vue, lainuri_ws, send_user_logging_in, abort_user_login} from '../lainuri'
import {LEUserLoginComplete, LEUserLoggingIn, LEUserLoginAbort} from '../lainuri_events'


let emited = 0
export default {
  name: 'BottomMenu',
  data: () => ({
    bottom_bar_view: undefined,
  }),
  created: function () {

  },
  methods: {
    abort_user_login: function () {
      console.log("abort_user_login in CheckOut")
      this.$data.user = undefined
      this.$emit('abort_user_login');
    },
    start_checking_out: function () {
      console.log("Started checking out")
    },
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
