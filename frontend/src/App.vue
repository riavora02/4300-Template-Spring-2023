<script setup lang="ts">
import Webtoon from './components/Webtoon.vue';
import { WebtoonProps } from './types';

const webtoonData: WebtoonProps[] = [
  {
    id: 1,
    title: "Webtoon 1",
    summary: "this is webtoon 1",
  },
  {
    id: 2,
    title: "Webtoon 2",
    summary: "this is webtoon 2",
  },
]
</script>

<template>
  <div className="container mx-auto p-6">
    <h1 className="text-3xl mb-3">Hello, world!</h1>
    <p>This is a paragraph.</p>
    <Webtoon v-for="webtoon in webtoonData" :id="webtoon.id" :title="webtoon.title" :summary="webtoon.summary" />
  </div>
</template>

<style scoped>
</style>
