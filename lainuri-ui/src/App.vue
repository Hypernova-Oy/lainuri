<template>
  <div id="app">
    <img alt="Vue logo" src="./assets/logo.png">
    <ul id="container_item_carousel">
      <md-card v-for="tag in rfid_tags_present" v-bind:key="tag.barcode" md-with-hover class="md-primary">
        <md-ripple>
          <md-card-media>
            <div class="md-title">
              <img class="cover_image" :src="tag.image_url" alt="Cover image"/>
            </div>
          </md-card-media>
          <md-card-header>
            <md-card-header-text>
              <div class="md-title  md-caption">{{tag.title}}</div>
              <div class="md-subhead">{{tag.author}}</div>
            </md-card-header-text>
          </md-card-header>
        </md-ripple>
      </md-card>
    </ul>
    <CheckOut v-if="app_mode === 'mode_checkout'" v-on:abort_user_login="abort_user_login"/>
    <md-button id="checkout_mode_button" class="md-raised md-primary md-display-4" v-on:click="enter_checkout_mode">LAINAA</md-button>
    <md-button id="checkin_mode_button" class="md-raised md-accent md-display-4" v-on:click="enter_checkin_mode">PALAUTA</md-button>
    <md-button class="md-raised">{{barcode_read}}<br/>{{rfid_tags_present}}</md-button>
  </div>
</template>

<script>
import CheckOut from './components/CheckOut.vue'
import {start_ws, lainuri_set_vue, lainuri_ws, send_user_logging_in, abort_user_login} from './lainuri'

export default {
  name: 'app',
  components: {
    CheckOut,
  },
  created: function () {
    this.$data.barcode_read = 'HASDHASHDAHSD';

    lainuri_set_vue(this);
    start_ws();
  },
  data: function () {
    return {
      name: 'Vue.js',
      app_mode: 'mode_main_menu',
      user: {},
      barcode_read: 'no bccc',
      rfid_tags_present: [{
        barcode: '167N00000001',
        image_url: 'https://i0.wp.com/www.lesliejonesbooks.com/wp-content/uploads/2017/01/cropped-FavIcon.jpg?fit=200%2C200&ssl=1',
        title: 'Grenades for Dummies',
        author: 'Olli-Antti Kivilahti',
      },{
        barcode: '167N11111111',
        image_url: 'https://synergydental.org.uk/wp-content/uploads/2019/06/Synergy-Favicon-90x90.png',
        title: 'Books for Dummies',
        author: 'Olli-Antti Kivilahti',
      },{
        barcode: '167222222222',
        image_url: 'https://papasfishandchips.com/wp-content/uploads/2018/03/FAVICON1-1.png',
        title: 'Fa ces for Dummies',
        author: 'Olli-Antti Kivilahti',
      }],
    }
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
    }
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

#checkout_mode_button {
  width: 49%;
  height: 200px;
}

#checkin_mode_button {
  width: 49%;
  height: 200px;
}

.md-card {
  width: 320px;
  margin: 4px;
  display: inline-block;
  vertical-align: top;
}

</style>
