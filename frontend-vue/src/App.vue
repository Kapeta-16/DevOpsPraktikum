<script setup lang="ts">
import { useUserStore } from "./stores/user";
import { useRouter } from "vue-router";
import { computed } from "vue";
import logoSvg from "./assets/logo.svg";

const userStore = useUserStore();
const router = useRouter();

const ordersLink = computed(() => {
  return userStore.admin ? "/admin/orders" : "/orders";
});

function logout() {
  userStore.logout();
  router.push("/");
}
</script>

<template>
  <nav class="navbar">
    <router-link to="/" class="brand">
      <img :src="logoSvg" alt="Zlatni Čips" class="brand-logo" />
      <span>Zlatni Čips</span>
    </router-link>
    <div class="nav-links">
      <template v-if="!userStore.username">
        <router-link to="/login" class="nav-link">Prijava</router-link>
      </template>
      <template v-else>
        <span class="welcome">
          {{ userStore.username }}
          <span v-if="userStore.admin" class="admin-badge">(Admin)</span>
        </span>
        <router-link :to="ordersLink" class="nav-link">Narudžbe</router-link>
        <button @click="logout" class="logout-btn">Odjava</button>
      </template>
    </div>
  </nav>
  <router-view />
</template>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background: linear-gradient(135deg, #104911 0%, #548C2F 100%);
  box-shadow: 0 2px 10px rgba(16, 73, 17, 0.3);
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.5em;
  font-weight: 700;
  color: white;
  text-decoration: none;
}

.brand-logo {
  width: 40px;
  height: 40px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 20px;
  transition: background 0.2s;
}

.nav-link:hover {
  background: rgba(249, 166, 32, 0.3);
}

.welcome {
  color: white;
  font-weight: 500;
}

.admin-badge {
  color: #FFD449;
  font-weight: 700;
  font-size: 0.85em;
  margin-left: 4px;
}

.logout-btn {
  background: #F9A620;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.95em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #FFD449;
  color: #104911;
}
</style>
