<template>
  <div>
    <h2>Menu</h2>
    <ul>
      <li v-for="item in menu" :key="item.ime">
        <b>{{ item.name }}</b> - {{ item.price_euro }} €
        <span v-if="item.description">({{ item.description }})</span>
      </li>
    </ul>
    <div v-if="error" style="color: red">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";

const menu = ref<any[]>([]);
const error = ref("");

onMounted(async () => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/meni`);
    if (!res.ok) throw new Error("Backend error");
    menu.value = await res.json();
  } catch (e: any) {
    error.value = e.message ?? "Could not load menu";
  }
});
</script>
