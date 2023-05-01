<script setup lang="ts">
import { WebtoonType } from "../types"

defineProps<{ webtoon: WebtoonType }>()
</script>

<template>
  <!-- <div class="card border border-gray-200 shadow-lg rounded-lg">
    <div class="card-body">
      <h2 class="card-title">Job Title</h2>
      <p>Rerum reiciendis beatae tenetur excepturi</p>
    </div>
  </div> -->
  <div class="card border border-gray-200 shadow-lg rounded-lg">
    <div class="card-body">
      <h2 class="card-title">
        <a :href="webtoon.url" target="_blank">{{ webtoon.title }}</a>
      </h2>
      <div class="p-6 text-slate-800">
        <p>{{ webtoon.summary }}</p>
        <p>{{ webtoon.released_date }}</p>
        <p>{{ webtoon.likes }}</p>
        <p>{{ webtoon.subscribe }}</p>
        <p>{{ webtoon.view }}</p>
        <p>{{ webtoon.sim }}</p>
      </div>
    </div>
    <!-- <div class="w-full p-4 bg-green-200">
        <h3 class="text-xl font-semibold text-center">{{ webtoon.title }}</h3>
        <h4>{{ webtoon.genre }}</h4>
      </div>
      <div class="p-6 text-slate-800">
        <p>{{ webtoon.summary }}</p>
        <p>{{ webtoon.released_date }}</p>
        <p>{{ webtoon.likes }}</p>
        <p>{{ webtoon.subscribe }}</p>
        <p>{{ webtoon.view }}</p>
        <p>{{ webtoon.sim }}</p>
      </div> -->
  </div>
</template>
