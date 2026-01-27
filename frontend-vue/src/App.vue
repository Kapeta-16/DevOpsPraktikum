<script setup lang="ts">
import { useUserStore } from "./stores/user";
const userStore = useUserStore();

function logout() {
  userStore.logout();
}
</script>

<template>
  <nav>
    <router-link to="/">Menu</router-link>
    <template v-if="!userStore.username">
      | <router-link to="/login">Login</router-link>
    </template>
    <template v-else>
      | Welcome, <b>{{ userStore.username }}</b> |
      <router-link to="/orders">Orders</router-link>
      <button @click="logout" style="margin-left: 1em">Logout</button>
    </template>
  </nav>
  <router-view />
</template>

<style scoped>
nav {
  margin-bottom: 2rem;
}
router-link {
  margin-right: 1rem;
}
button {
  font-size: 1em;
}
</style>
