<script setup lang="ts">
import axios from "axios"
import WebtoonList from "./components/WebtoonList.vue"
import LoadingSpinner from "./components/LoadingSpinner.vue"
import InputDisplay from "./components/InputDisplay.vue"

import { WebtoonType } from "./types"
import { onMounted, ref } from "vue"

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

const webtoons = ref<WebtoonType[]>([])
const genres = ref<string[]>([])
const searchText = ref("")
const genreFilter = ref("all")
const nichenessValue = ref(50)
const loadingResults = ref(false)
const activeTab = ref(0)
const nothingText = ref("")
const searched = ref(false)

const additionalWebtoons = ref<WebtoonType[]>([])

const elem = ref<null | HTMLDivElement>(null)
const top = ref<null | HTMLDivElement>(null)

const scrollToTop = () => {
  top.value?.scrollIntoView({ behavior: "smooth" })
}

const searchQuery = async () => {
  searched.value = true
  elem.value?.scrollIntoView({ behavior: "smooth" })

  const request = `${BACKEND_URL}/webtoons?q=${searchText.value}&genre=${
    genreFilter.value
  }&num=${100 - nichenessValue.value}`
  loadingResults.value = true
  axios
    .get(request)
    .then((res) => {
      webtoons.value = res.data["webtoons"]
      if (res.data["all"]) {
        additionalWebtoons.value = res.data["all"]
      }

      if (genreFilter.value == "all") {
        activeTab.value = 0
      } else {
        activeTab.value = 1
      }

      if (webtoons.value.length == 0 && webtoons.value.length == 0) {
        nothingText.value =
          "No webtoons found for this search! Please try a different search."
      }

      loadingResults.value = false
    })
    .catch((err) => {
      console.log(err)
    })
}

onMounted(() => {
  const request = `${BACKEND_URL}/genres`
  axios
    .get(request)
    .then((res) => {
      genres.value = res.data["genres"]
    })
    .catch((err) => {
      console.log(err)
    })
})
</script>

<template>
  <button
    class="btn btn-circle btn-accent fixed z-10 bottom-10 right-10 text-white"
    @click="scrollToTop"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke-width="1.5"
      stroke="currentColor"
      class="w-6 h-6"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M12 19.5v-15m0 0l-6.75 6.75M12 4.5l6.75 6.75"
      />
    </svg>
  </button>
  <div
    ref="top"
    class="hero min-h-screen max-h-screen bg-[url('./assets/dots.png')] relative"
  >
    <div
      class="bg-[url('./assets/big-speech-bubble.svg')] absolute top-0 left-0 w-2/3 h-2/3 bg-contain bg-no-repeat bg-center flex justify-center place-items-center"
    ></div>
    <div
      class="bg-[url('./assets/small-speech-bubble.svg')] absolute w-2/3 h-1/2 bottom-0 right-0 bg-contain bg-center bg-no-repeat flex justify-center place-items-center"
    >
      <form
        class="flex flex-col gap-5 relative top-[-2em] w-2/3"
        @submit.prevent="searchQuery"
      >
        <label for="simple-search" class="sr-only">Search</label>
        <input
          type="text"
          placeholder="What kind of Webtoon would you like to read?"
          class="input input-bordered"
          v-model="searchText"
        />
        <div class="grid grid-flow-col gap-5 justify-stretch items-center">
          <div class="basis-10">
            <select
              v-model="genreFilter"
              id="genre"
              class="select select-bordered p-2.5 w-full"
            >
              <option value="all" selected>All genres</option>
              <option v-for="genre in genres" :value="genre" :key="genre">
                {{ genre }}
              </option>
            </select>
          </div>
          <div class="form-control">
            <label class="label">
              <span class="label-text">Nicheness</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              v-model="nichenessValue"
              class="range range-accent"
            />
          </div>
          <div>
            <button
              type="submit"
              class="btn text-lg btn-accent font-medium text-white"
            >
              <svg
                class="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                ></path>
              </svg>
              <span class="sr-only">Search</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>

  <div ref="elem" class="container mx-auto min-h-screen px-6 py-10 font-body">
    <p v-show="!searched">Search for a webtoon above!</p>
    <div class="flex flex-col space-y-8">
      <InputDisplay
        :query="searchText"
        :genre="genreFilter"
        :nicheness="nichenessValue"
        v-show="webtoons.length > 0 || nothingText"
      />

      <div>
        <div v-if="!loadingResults">
          <div v-if="webtoons.length > 0">
            <div class="tabs mb-5">
              <a
                href="#"
                class="tab tab-bordered"
                :class="{ 'tab-active': activeTab == 0 }"
                @click.prevent="activeTab = 0"
                >Top Recommended</a
              >
              <a
                href="#"
                class="tab tab-bordered"
                :class="{ 'tab-active': activeTab == 1 }"
                @click.prevent="activeTab = 1"
                >Recommended by Genre Filter</a
              >
            </div>
            <WebtoonList
              class="mb-20"
              :webtoons="webtoons"
              title="Recommended Webtoons based on query similarity"
              v-show="activeTab == 0"
            />
            <WebtoonList
              :webtoons="additionalWebtoons"
              title="Recommended Webtoons based on input genre filter"
              v-show="activeTab == 1"
            />
          </div>
          <div v-else>
            {{ nothingText }}
          </div>
        </div>
        <div class="flex justify-center" v-else>
          <LoadingSpinner />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
