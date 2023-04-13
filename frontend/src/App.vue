<script setup lang="ts">
import axios from 'axios';
import Webtoon from './components/Webtoon.vue';
import { WebtoonType } from './types';
import { onMounted, ref } from 'vue';

const BACKEND_URL = "http://4300showcase.infosci.cornell.edu:4539"

const webtoons = ref<WebtoonType[]>()

onMounted(async () => {
  axios.get(`${BACKEND_URL}/webtoons`).then((res) => {
    console.log(res.data)
    webtoons.value = res.data
  }).catch((err) => {
    console.log(err)
  })
})

</script>

<template>
  <div class="container mx-auto p-6">
    <h1 class="text-3xl mb-3">Hello, world!</h1>
    <p>This is a paragraph.</p>
    <Webtoon v-for="webtoon in webtoons" :id="webtoon.id" :title="webtoon.title" :summary="webtoon.summary" class="mb-6" />
  </div>
</template>

<style scoped>
</style>
