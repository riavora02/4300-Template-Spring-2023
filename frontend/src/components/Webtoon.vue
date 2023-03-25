<script setup lang="ts">
import { WebtoonProps } from '../types'

defineProps<WebtoonProps>()

</script>

<template>
    <div>
        <h3 class="font-bold text-lg">{{ title }}</h3>
        <p>{{ summary }}</p>
    </div>
</template>