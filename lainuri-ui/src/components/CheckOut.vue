<template>
  <div class="checkout_component">
    <md-card class="md-accent" md-with-hover>
      <md-ripple>
        <md-card-header>
          <div class="md-title">Please read the library card</div>
        </md-card-header>
        <md-card-content v-if="user">
          Welcome {{user.firstname}}!
        </md-card-content>
        <md-card-actions>
          <md-button>Help!</md-button>
          <md-button v-on:click="$emit('abort_user_login')">Return</md-button>
        </md-card-actions>
      </md-ripple>
    </md-card>
  </div>
</template>

<script>

export default {
  name: 'CheckOut',
  props: {
    user: Object,
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
