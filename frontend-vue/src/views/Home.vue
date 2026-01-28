<template>
  <div class="home">
    <!-- Header Image -->
    <section class="header-banner">
      <img :src="headerImg" alt="Zlatni Čips" class="header-image" />
    </section>

    <!-- Menu Section -->
    <section class="menu-section">
      <h2 class="section-title">Naš Meni</h2>
      
      <div v-if="loading" class="loading">Učitavanje menija...</div>
      <div v-if="error" class="error-message">{{ error }}</div>
      
      <div v-if="!loading && menu.length" class="menu-grid">
        <div v-for="item in menu" :key="item.id || item.ime" class="menu-card">
          <img 
            :src="getItemImage(item.id)" 
            :alt="item.name || item.ime" 
            class="menu-item-image"
          />
          <div class="menu-card-content">
            <h3 class="item-name">{{ item.name || item.ime }}</h3>
            <p v-if="item.description || item.opis" class="item-description">
              {{ item.description || item.opis }}
            </p>
            <div class="item-footer">
              <span class="item-price">{{ item.price_euro || item.cijena }} €</span>
              <button 
                v-if="userStore.username" 
                class="add-btn"
                @click="addToCart(item)"
                title="Dodaj u košaricu"
              >
                🛒
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!loading && !menu.length && !error" class="no-items">
        Meni trenutno nije dostupan.
      </div>
    </section>

    <!-- Cart Section -->
    <div v-if="cart.length" class="cart-floating">
      <div class="cart-header" @click="cartOpen = !cartOpen">
        <span class="cart-icon">🛒</span>
        <span class="cart-count">{{ cartItemCount }}</span>
        <span class="cart-total">{{ cartTotal.toFixed(2) }} €</span>
        <span class="cart-toggle">{{ cartOpen ? '▼' : '▲' }}</span>
      </div>
      
      <div v-if="cartOpen" class="cart-body">
        <div v-for="(item, idx) in cart" :key="idx" class="cart-item">
          <span class="cart-item-name">{{ item.name || item.ime }}</span>
          <span class="qty">{{ item.kolicina }}</span>
          <span class="cart-item-price">{{ ((item.price_euro || item.cijena) * item.kolicina).toFixed(2) }} €</span>
          <button class="remove-btn" @click="removeFromCart(idx)">✕</button>
        </div>
        
        <div class="cart-actions">
          <button class="order-btn" @click="placeOrder" :disabled="ordering">
            {{ ordering ? 'Naručujem...' : 'Naruči' }}
          </button>
        </div>
        
        <div v-if="orderSuccess" class="order-success">
          Narudžba uspješno poslana! ETA: {{ orderEta }}
        </div>
        <div v-if="orderError" class="order-error">{{ orderError }}</div>
      </div>
    </div>

    <!-- Login prompt for guests -->
    <div v-if="!userStore.username" class="login-prompt">
      <p>Prijavite se za naručivanje</p>
      <router-link to="/login" class="login-link">Prijava</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useUserStore } from "../stores/user";
import logoSvg from "../assets/logo.svg";
import headerImg from "../assets/header.png";

const userStore = useUserStore();

// Import all images from assets folder
const imageModules = import.meta.glob('../assets/*.jpg', { eager: true, import: 'default' }) as Record<string, string>;

// Function to get image by item id
function getItemImage(itemId: string): string {
  const imagePath = `../assets/${itemId}.jpg`;
  return imageModules[imagePath] || logoSvg;
}

const menu = ref<any[]>([]);
const cart = ref<any[]>([]);
const loading = ref(true);
const error = ref("");
const cartOpen = ref(true);
const ordering = ref(false);
const orderSuccess = ref(false);
const orderError = ref("");
const orderEta = ref("");

const cartItemCount = computed(() => {
  return cart.value.reduce((sum, item) => sum + item.kolicina, 0);
});

const cartTotal = computed(() => {
  return cart.value.reduce((sum, item) => {
    return sum + (item.price_euro || item.cijena) * item.kolicina;
  }, 0);
});

function addToCart(item: any) {
  const existing = cart.value.find(
    (c) => (c.name || c.ime) === (item.name || item.ime)
  );
  if (existing) {
    existing.kolicina++;
  } else {
    cart.value.push({
      ...item,
      ime: item.name || item.ime,
      cijena: item.price_euro || item.cijena,
      kolicina: 1,
    });
  }
}

function removeFromCart(idx: number) {
  cart.value.splice(idx, 1);
}

async function placeOrder() {
  if (!userStore.username || cart.value.length === 0) return;

  ordering.value = true;
  orderError.value = "";
  orderSuccess.value = false;

  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/narudba`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: userStore.username,
        items: cart.value.map((item) => ({
          ime: item.ime,
          cijena: item.cijena,
          kolicina: item.kolicina,
        })),
      }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Greška pri narudžbi");

    orderSuccess.value = true;
    orderEta.value = data.eta_delivery
      ? new Date(data.eta_delivery).toLocaleTimeString()
      : "~45 min";
    cart.value = [];
  } catch (e: any) {
    orderError.value = e.message;
  } finally {
    ordering.value = false;
  }
}

onMounted(async () => {
  loading.value = true;
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/meni`);
    if (!res.ok) throw new Error("Ne mogu učitati meni");
    menu.value = await res.json();
  } catch (e: any) {
    error.value = e.message ?? "Greška pri učitavanju menija";
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: white;
}

/* Header Banner */
.header-banner {
  width: 100vw;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(16, 73, 17, 0.2);
}

.header-image {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

/* Menu Section */
.menu-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.section-title {
  text-align: center;
  font-size: 2em;
  color: #104911;
  margin-bottom: 30px;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.menu-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(16, 73, 17, 0.25), 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.menu-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 35px rgba(249, 166, 32, 0.4), 0 4px 12px rgba(0, 0, 0, 0.15);
}

.menu-item-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  background-color: white;
  flex-shrink: 0;
}

.menu-card-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.item-name {
  margin: 0 0 10px 0;
  font-size: 1.3em;
  color: #104911;
}

.item-description {
  color: #666;
  font-size: 0.95em;
  line-height: 1.4;
  flex: 1;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.item-price {
  font-size: 1.4em;
  font-weight: 700;
  color: #F9A620;
}

.add-btn {
  background: #104911;
  color: white;
  border: none;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  font-size: 1.2em;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 3px 10px rgba(16, 73, 17, 0.3);
}

.add-btn:hover {
  background: #548C2F;
  transform: scale(1.1);
  box-shadow: 0 5px 15px rgba(84, 140, 47, 0.4);
}

/* Cart */
.cart-floating {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 350px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(16, 73, 17, 0.25);
  overflow: hidden;
  z-index: 1000;
  border: 2px solid #F9A620;
}

.cart-header {
  background: #F9A620;
  color: white;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.cart-icon {
  font-size: 1.3em;
}

.cart-count {
  background: white;
  color: #F9A620;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.9em;
}

.cart-total {
  flex: 1;
  text-align: right;
  font-weight: 700;
  font-size: 1.1em;
}

.cart-toggle {
  font-size: 0.8em;
}

.cart-body {
  padding: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.cart-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #AAB03C;
}

.cart-item-name {
  flex: 1;
  font-weight: 500;
}

.cart-item-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.qty-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: #FFD449;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1em;
  font-weight: 700;
  color: #104911;
}

.qty-btn:hover {
  background: #F9A620;
  color: white;
}

.qty {
  min-width: 20px;
  text-align: center;
  font-weight: 600;
}

.cart-item-price {
  font-weight: 600;
  color: #F9A620;
  min-width: 60px;
  text-align: right;
}

.remove-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 1.1em;
}

.remove-btn:hover {
  color: #104911;
}

.cart-actions {
  margin-top: 15px;
}

.order-btn {
  width: 100%;
  background: #104911;
  color: white;
  border: none;
  padding: 15px;
  border-radius: 10px;
  font-size: 1.1em;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}

.order-btn:hover:not(:disabled) {
  background: #548C2F;
}

.order-btn:disabled {
  background: #AAB03C;
  cursor: not-allowed;
}

.order-success {
  margin-top: 15px;
  padding: 12px;
  background: #548C2F;
  color: white;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}

.order-error {
  margin-top: 15px;
  padding: 12px;
  background: #f8d7da;
  color: #721c24;
  border-radius: 8px;
  text-align: center;
}

/* Login Prompt */
.login-prompt {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: white;
  padding: 20px 30px;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(16, 73, 17, 0.25);
  text-align: center;
  border: 2px solid #F9A620;
}

.login-prompt p {
  margin: 0 0 10px 0;
  color: #666;
}

.login-link {
  display: inline-block;
  background: #F9A620;
  color: white;
  padding: 10px 25px;
  border-radius: 25px;
  text-decoration: none;
  font-weight: 600;
  transition: background 0.2s;
}

.login-link:hover {
  background: #FFD449;
  color: #104911;
}

/* Loading & Error */
.loading {
  text-align: center;
  padding: 40px;
  color: #104911;
  font-size: 1.1em;
}

.error-message {
  text-align: center;
  padding: 20px;
  background: #f8d7da;
  color: #721c24;
  border-radius: 10px;
  margin: 20px 0;
}

.no-items {
  text-align: center;
  padding: 40px;
  color: #104911;
}
</style>
