<script setup lang="ts">
import { WebtoonListProps } from "../types"
import Webtoon from "./Webtoon.vue"

defineProps<WebtoonListProps>()
</script>

<template>
  <div>
    <h4 class="text-2xl font-display">{{ title }}</h4>
    <p class="mt-10" v-if="webtoons.length == 0">
      No webtoons found for this category.
    </p>
    <div class="mt-10 grid grid-flow-row auto-rows-max gap-10">
      <div
        class="indicator w-full"
        v-for="(webtoon, index) in webtoons.slice(0, 3)"
      >
        <span
          class="indicator-item text-white"
          :class="{
            'indicator-start': index % 2 == 0,
          }"
        >
          <span
            class="w-12 h-12 text-xl rounded-full grid place-items-center"
            :class="{
              'bg-amber-400': index == 0,
              'bg-zinc-400': index == 1,
              'bg-yellow-700': index == 2,
            }"
            >{{ index + 1 }}</span
          >
        </span>
        <div class="flex border border-gray-200 shadow-lg rounded-xl w-full">
          <div class="flex-none w-72 relative rounded-l-xl" v-show="index != 1">
            <img
              src="../assets/num1.png"
              alt=""
              class="absolute inset-0 w-full h-full rounded-l-xl object-cover"
              loading="lazy"
              v-if="index == 0"
            />
            <img
              src="../assets/num3.png"
              alt=""
              class="absolute inset-0 w-full h-full rounded-l-xl object-cover"
              loading="lazy"
              v-else-if="index == 2"
            />
          </div>
          <Webtoon
            :webtoon="webtoon"
            class="flex-auto text-white"
            :class="{
              'bg-red-500 rounded-r-xl': index % 2 == 0,
              'bg-blue-500 rounded-l-xl': index % 2 == 1,
            }"
          />
          <div class="flex-none w-72 relative rounded-r-xl" v-show="index == 1">
            <img
              src="../assets/num2.png"
              alt=""
              class="absolute inset-0 w-full h-full rounded-r-xl object-cover"
              loading="lazy"
            />
          </div>
        </div>
      </div>
    </div>
    <div class="mt-10 grid grid-cols-2 gap-10" v-show="webtoons.length > 3">
      <div
        class="indicator w-full"
        v-for="(webtoon, index) in webtoons.slice(3)"
      >
        <span class="indicator-item indicator-start">
          <span
            class="w-12 h-12 text-xl rounded-full bg-slate-500 grid place-items-center text-white"
            >{{ index + 4 }}</span
          >
        </span>
        <Webtoon
          :webtoon="webtoon"
          class="card border border-gray-200 shadow-lg rounded-xl w-full"
        />
      </div>
    </div>
  </div>
</template>
