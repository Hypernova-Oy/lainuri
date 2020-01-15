<template>
  <div class="checkin_container">
    <md-card class="md-accent" md-with-hover>
      <md-ripple>
        <md-card-header v-if="! user.cardnumber">
          <div class="md-title">checking in</div>
        </md-card-header>
        <md-card-actions>
          <md-button>Help!</md-button>
          <md-button v-on:click="abort_user_login" v-if="!user.cardnumber" class="md-raised md-accent md-display-4">Return</md-button>
        </md-card-actions>
      </md-ripple>
    </md-card>
  </div>
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
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
