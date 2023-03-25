<script setup lang="ts">
import { WebtoonProps } from '../types'

defineProps<WebtoonProps>()

</script>

<template>
    <div>
        <h3>{{ title }}</h3>
        <p>{{ summary }}</p>
    </div>
</template>