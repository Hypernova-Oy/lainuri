<template>
  <v-menu top>
    <template v-slot:activator="{ on }">
      <div class="lang-menu-open-container">
        <v-img
          :alt="active_language_2_char" :src="'images/flags/64/'+active_language_2_char.toUpperCase()+'.png'"
          v-on="on"
          width="128px"
          height="128px"
        />
        <v-icon x-large dark class="lang-menu-dropdown-icon">
          mdi-dots-vertical
        </v-icon>
      </div>
    </template>
    <v-list>
      <v-list-item
        v-for="(lang) in $appConfig.i18n.enabled_locales"
        :key="lang"
        @click="set_lo(lang)"
      >
        <v-img
          :key="lang"
          :alt="lang" :src="'images/flags/64/'+lang.toUpperCase()+'.png'"
        />
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script>

import {lainuri_ws} from '../lainuri'
import {LELocaleSet} from '../lainuri_events'

export default {
  name: 'LanguagePicker',
  computed: {
    active_language_2_char: function () {
      return this.$appConfig.i18n.default_locale.substring(0,2);
    }
  },
  methods: {
    set_lo: function (lang_2_char) {
      lainuri_ws.dispatch_event(new LELocaleSet(this.$appConfigSetLocale(lang_2_char), 'client', 'server'))
    },
  }
}
</script>

<style scoped>
.lang-menu-open-container {
  position: relative;
}
.lang-menu-open-container .lang-menu-dropdown-icon {
  position: absolute;
  bottom: 42px;
  left: 114px;
}
</style>
