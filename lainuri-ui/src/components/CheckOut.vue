<template>
  <v-container centered>
    <v-card ripple raised>
      <v-card-title v-if="! user.cardnumber">Please read the library card</v-card-title>
      <v-card-title v-if="user.cardnumber">Welcome {{user.firstname}}!</v-card-title>

      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn text v-on:click="abort_user_login" v-if="!user.cardnumber" large color="secondary">
          Return
        </v-btn>

        <v-btn text v-on:click="abort_user_login" v-if="user.cardnumber" large color="primary">
          Logout
        </v-btn>

        <v-btn text>
          Help
        </v-btn>
      </v-card-actions>
    </v-card>

  </v-container>
</template>

<script>
import {start_ws, lainuri_set_vue, lainuri_ws, send_user_logging_in, abort_user_login} from '../lainuri'
import {LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed} from '../lainuri_events'


export default {
  name: 'CheckOut',
  props: {
    user: Object,
  },
  methods: {
    abort_user_login: function () {
      console.log("abort_user_login in CheckOut")
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
