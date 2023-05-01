<script setup lang="ts">
import axios from "axios"
import WebtoonList from "./components/WebtoonList.vue"
import LoadingSpinner from "./components/LoadingSpinner.vue"
import SplashView from "./components/SplashView.vue"
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

const additionalWebtoons = ref<WebtoonType[]>([])

const searchQuery = async () => {
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
  <SplashView />
  <div class="container mx-auto min-h-screen px-6 py-20 font-lato">
    <div class="flex flex-col space-y-8">
      <h1
        class="text-center text-6xl mb-0 font-semibold font-display font-lexend"
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
              placeholder="What kind of Webtoon do you want...?"
              class="input input-bordered rounded-full input-accent w-full pl-10 p-2.5"
              required
            />

            <!-- <input
              type="text"
              v-model="searchText"
              class="text-lg bg-gray-50 border border-gray-300 text-gray-900 rounded-full focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2.5"
              placeholder="Search for a Webtoon..."
              required
            /> -->
          </div>
          <div>
            <select
              v-model="genreFilter"
              id="genre"
              class="select select-bordered w-full p-2.5"
            >
              <option value="all" selected>All genres</option>
              <option v-for="genre in genres" :value="genre" :key="genre">
                {{ genre }}
              </option>
            </select>
          </div>
          <div>
            <input
              type="range"
              min="0"
              max="100"
              v-model="nichenessValue"
              class="range range-accent"
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

      <div>
        <div v-if="!loadingResults">
          <div v-show="webtoons.length > 0">
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
              title="Additional Webtoons based on input filter"
              v-show="activeTab == 1"
            />
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
