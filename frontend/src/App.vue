<script setup lang="ts">
import axios from "axios"
import Webtoon from "./components/Webtoon.vue"
import { WebtoonType } from "./types"
import { ref } from "vue"

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

const webtoons = ref<WebtoonType[]>([])
const searchText = ref("")

const searchQuery = async () => {
  const request = `${BACKEND_URL}/webtoons?q=${searchText.value}`
  axios
    .get(request)
    .then((res) => {
      webtoons.value = res.data["webtoons"]
      console.log(webtoons.value)
    })
    .catch((err) => {
      console.log(err)
    })
}
</script>

<template>
  <div class="container mx-auto px-6 py-20 font-lato">
    <div class="flex flex-col space-y-12">
      <h1
        class="text-center text-6xl mb-0 font-semibold font-display text-slate-700 font-lexend"
      >
        Webtoon Finder
      </h1>

      <div class="md:mx-52">
        <form class="flex items-center" @submit.prevent="searchQuery">
          <label for="simple-search" class="sr-only">Search</label>
          <div class="relative w-full">
            <div
              class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none"
            >
              <svg
                aria-hidden="true"
                class="w-5 h-5 text-gray-500 dark:text-gray-400"
                fill="currentColor"
                viewBox="0 0 20 20"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  fill-rule="evenodd"
                  d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                  clip-rule="evenodd"
                ></path>
              </svg>
            </div>
            <input
              type="text"
              v-model="searchText"
              class="text-lg bg-gray-50 border border-gray-300 text-gray-900 rounded-full focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2.5"
              placeholder="Search for a Webtoon..."
              required
            />
          </div>
          <button
            type="submit"
            class="p-2.5 ml-2 text-lg font-medium text-white bg-green-700 rounded-lg border border-green-700 hover:bg-green-800 focus:ring-4 focus:outline-none focus:ring-green-300"
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
        </form>
      </div>

      <div class="mt-20 grid grid-cols-3 gap-8">
        <Webtoon
          v-for="webtoon in webtoons"
          :id="webtoon.id"
          :title="webtoon.title"
          :summary="webtoon.summary"
          class="mb-6"
        />
      </div>
    </div>
  </div>
</template>

<style scoped></style>
