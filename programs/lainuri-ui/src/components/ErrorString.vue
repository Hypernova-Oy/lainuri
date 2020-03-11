<template>
  <span>{{exception_summary}}</span>
</template>

<script>
import {ItemBib} from '../item_bib.js'
import {translate_exception} from '../exception.js'

export default {
  name: 'ErrorString',
  props: {
    item_bib: ItemBib,
  },
  data: () => ({
  }),
  computed: {
    exception_summary: function () {
      let e_str = '';
      if (this.item_bib.states_check_inout) e_str += translate_exception(this.$getGlobalize(), this.item_bib.states_check_inout);
      if (this.item_bib.states_set_tag_alarm) e_str += translate_exception(this.$getGlobalize(), this.item_bib.states_set_tag_alarm);
      if (!e_str) e_str = '<UNKNOWN_EXCEPTION_SUMMARY>'
      return e_str;
    },
  },
}
</script>

<style scoped>

</style>
