<script setup lang="ts">
import { WebtoonListProps } from "../types"
import Webtoon from "./Webtoon.vue"

defineProps<WebtoonListProps>()
</script>

<template>
  <div>
    <h4 class="text-2xl" v-if="webtoons.length > 0">{{ title }}</h4>
    <div class="mt-10 grid grid-flow-row auto-rows-max gap-8">
      <div
        class="indicator w-full"
        v-for="(webtoon, index) in webtoons.slice(0, 3)"
      >
        <span
          class="indicator-item"
          :class="{ 'indicator-start': index % 2 == 0 }"
        >
          <span
            class="w-10 h-10 text-xl rounded-full bg-gray-400 grid place-items-center"
            >{{ index + 1 }}</span
          >
        </span>
        <Webtoon :webtoon="webtoon" class="w-full" />
      </div>
    </div>
    <div class="mt-10 grid grid-cols-2 gap-8" v-show="webtoons.length > 3">
      <div
        class="indicator w-full"
        v-for="(webtoon, index) in webtoons.slice(3)"
      >
        <span
          class="indicator-item"
          :class="{
            'indicator-start': index % 2 == 0,
            'indicator-bottom': index % 2 == 1,
          }"
        >
          <span
            class="w-10 h-10 text-xl rounded-full bg-gray-400 grid place-items-center"
            >{{ index + 4 }}</span
          >
        </span>
        <Webtoon :webtoon="webtoon" class="w-full" />
      </div>
    </div>
  </div>
</template>
