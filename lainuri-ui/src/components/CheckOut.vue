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


let emited = 0
export default {
  name: 'CheckOut',
  data: function () {
    return {
      user: Object,
    }
  },
  created: function () {
    lainuri_ws.attach_event_listener(LEUserLoggedIn, (event) => {
      console.log(`Received event '${LEUserLoggedIn.name}'`);
      this.$data.user = event;
    });

    if (emited) {
    lainuri_ws.dispatch_event(
      new LEUserLoggedIn('Olli-Antti', 'Kivilahti', '167A01010101', 'server', 'client', 'user-logged-in-tzzzt')
    );
    }
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
