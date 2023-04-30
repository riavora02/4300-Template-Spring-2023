<script setup lang="ts">
import { WebtoonListProps } from "../types"
import Webtoon from "./Webtoon.vue"

defineProps<WebtoonListProps>()
</script>

<template>
  <div>
    <h4 class="text-2xl" v-if="webtoons.length > 0">{{ title }}</h4>
    <div class="mt-10 grid grid-cols-3 gap-6">
      <Webtoon
        v-for="webtoon in webtoons"
        :id="webtoon.id"
        :title="webtoon.title"
        :summary="webtoon.summary"
        :webtoon_id="webtoon.id"
        :thumbnail="webtoon.thumbnail"
        :genre="webtoon.genre"
        class="mb-6"
      />
    </div>
  </div>
</template>
