<template>
  <v-container centered>
    <v-card ripple raised>
      <v-card-title>Checking in</v-card-title>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text v-on:click="abort_user_login">
          Return
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script>
import {start_ws, lainuri_set_vue, lainuri_ws, send_user_logging_in, abort_user_login} from '../lainuri'
import {LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed} from '../lainuri_events'


let emited = 0
export default {
  name: 'CheckIn',
  data: function () {
    return {
      user: Object,
    }
  },
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
