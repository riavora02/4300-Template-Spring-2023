<script setup lang="ts">

interface WebtoonProps {
    title: string
    summary: string
}

defineProps<WebtoonProps>()

</script>

<template>
    <div>
        <h3>{{ title }}</h3>
        <p>{{ summary }}</p>
    </div>
</template>