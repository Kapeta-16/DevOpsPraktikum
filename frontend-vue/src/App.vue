<script setup lang="ts">
import { useUserStore } from "./stores/user";
import { useRouter } from "vue-router";
import { computed } from "vue";
import logoSvg from "./assets/logo.svg";
import cornerImg from "./assets/corner.png";

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
  <main class="main-content">
    <router-view />
  </main>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-left"> 
        <div class="footer-info">
          <span class="footer-brand">Zlatni Čips</span>
          <p class="footer-address">📍 Ulica Dobrog Okusa 42, Zagreb</p>
          <p class="footer-hours">🕐 Pon - Ned: 10:00 - 22:00</p>
          <p class="footer-phone">📞 +385 1 234 5678</p>
          <p class="footer-copyright">© 2026 Zlatni Čips. Sva prava pridržana.</p>
        </div>
      </div>
      <div class="footer-right">
        <img :src="cornerImg" alt="Zlatni Čips" class="footer-corner-img" />
      </div>
    </div>
  </footer>
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

.main-content {
  min-height: calc(100vh - 300px);
}

.footer {
  background: linear-gradient(135deg, #104911 0%, #548C2F 100%);
  color: white;
  padding: 10px 20px;
  margin-top: auto;
  position: relative;
  overflow: hidden;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.footer-left {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.footer-logo {
  width: 80px;
  height: 80px;
}

.footer-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-brand {
  font-size: 2em;
  font-weight: 700;
  margin-bottom: 10px;
}

.footer-right {
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
}

.footer-corner-img {
  width: 300px;
  height: auto;
  object-fit: contain;
  border-radius: 12px;
}

.footer-address,
.footer-hours,
.footer-phone {
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  font-size: 1em;
}

.footer-copyright { 
  font-size: 0.85em;
  color: rgba(255, 255, 255, 0.7);
}
</style>
