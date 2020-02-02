<template>
  <div id="arrowAnim">
    <div class="arrowSliding delay0">
      <div class="arrow"></div>
    </div>
    <div class="arrowSliding delay1">
      <div class="arrow"></div>
    </div>
    <div class="arrowSliding delay2">
      <div class="arrow"></div>
    </div>
    <div class="arrowSliding delay3">
      <div class="arrow"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ArrowSliding',
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#arrowAnim {
  width: 100vw;
  height: 55vh;
  display: flex;
  justify-content: center;
  align-items: flex-end;
}
#arrowAnim .arrow {
  width: 15vw;
  height: 15vw;
  border: 3vw solid;
  border-color: black transparent transparent black;
  transform: rotate(-135deg);
}
#arrowAnim .arrowSliding {
  opacity: 0;
  position: absolute;
  animation: slide 4s linear infinite;
}
#arrowAnim .delay0 {
    animation-delay: 0s;
}
#arrowAnim .delay1 {
    animation-delay: 1s;
}
#arrowAnim .delay2 {
    animation-delay: 2s;
}
#arrowAnim .delay3 {
    animation-delay: 3s;
}
@keyframes slide {
    0% { opacity:0; transform: translateY(-15vw); }
   20% { opacity:1; transform: translateY(-9vw); }
   80% { opacity:1; transform: translateY(+9vw); }
  100% { opacity:0; transform: translateY(+21vw); }
}
</style>
