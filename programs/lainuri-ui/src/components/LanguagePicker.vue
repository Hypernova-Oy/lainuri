<template>
  <v-menu top>
    <template v-slot:activator="{ on }">
      <div class="lang-menu-open-container">
        <v-img
          :alt="active_language_2_char" :src="'images/flags/64/'+active_language_2_char.toUpperCase()+'.png'"
          v-on="on"
        />
        <v-icon x-large dark class="lang-menu-dropdown-icon">
          mdi-dots-vertical
        </v-icon>
      </div>
    </template>
    <v-list>
      <v-list-item
        v-for="(lang) in enabled_languages"
        :key="lang"
        @click="set_language(lang)"
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
export default {
  name: 'LanguagePicker',
  data: () => ({
    active_language_2_char: 'en',
    enabled_languages: ['fi', 'en', 'ru', 'se'],
  }),
  methods: {
    set_language: function (lang_2_char) {
      this.$setLocale(lang_2_char)
      this.$data.active_language_2_char = lang_2_char
    },
  }
}
</script>

<style scoped>

</style>
