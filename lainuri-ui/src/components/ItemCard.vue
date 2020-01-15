<template>
  <md-card md-with-hover class="md-primary">
    <md-ripple>
      <md-card-media>
        <div class="md-title">
          <div class="cover_image_container">
            <img v-if="item_bib.book_cover_url" class="cover_image" :src="item_bib.book_cover_url" alt="Cover image"/>
            <img v-if="!item_bib.book_cover_url" class="cover_image" src="https://findicons.com/files/icons/1714/dropline_neu/128/image_missing.png" alt="Cover image"/>
          </div>
        </div>
      </md-card-media>
      <md-card-header>
        <md-card-header-text>
          <div class="md-title md-caption">{{item_bib.title || '...'}}</div>
          <div class="md-subhead author">{{item_bib.author || 'x'}}</div>
          <div class="md-subhead edition">{{item_bib.edition || '...'}}</div>
        </md-card-header-text>
      </md-card-header>
      <md-card-content>
        <div class="barcode">{{item_bib.barcode}}</div>
      </md-card-content>
    </md-ripple>
  </md-card>
</template>

<script>

export default {
  name: 'CheckOut',
  props: {
    item_bib: Object,
  },
}
</script>

<style scoped>
.md-card {
  width: 320px;
  height: 550px;
  margin: 4px;
  display: inline-block;
  vertical-align: top;
}
.cover_image_container {
  height: 400px;
  position: relative;
}
.cover_image {
  margin: 0;
  position: absolute;
  top: 50%;
  left: 0%;
  -ms-transform: translateY(-50%);
  transform: translateY(-50%);
}
</style>
