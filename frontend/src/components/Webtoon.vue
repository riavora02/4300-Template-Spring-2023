<script setup lang="ts">
import { WebtoonProps } from "../types"

defineProps<WebtoonProps>()
</script>

<template>
  <div class="border border-gray-200 shadow-lg rounded-lg">
    <div class="w-full p-4 bg-green-200">
      <h3 class="text-xl font-semibold text-center">{{ title }}</h3>
    </div>
    <div class="p-6 text-slate-800">
      <p>{{ summary }}</p>
    </div>
  </div>
</template>
