<script setup lang="ts">
import { InputDisplayProps } from "../types"

defineProps<InputDisplayProps>()
</script>

<template>
  <div class="card w-full bg-base-100 border border-slate-300">
    <div class="card-body text-center">
      <h2 class="card-title justify-center">{{ query }}</h2>
      <p><strong>Genre:</strong> {{ genre }}</p>
      <p><strong>Nicheness:</strong> {{ nicheness }}</p>
    </div>
  </div>
</template>
