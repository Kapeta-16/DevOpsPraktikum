<template>
  <div class="admin-orders">
    <h2>All Orders (Admin)</h2>
    <div v-if="error" class="error-message">{{ error }}</div>
    
    <div v-if="orders.length" class="orders-list">
      <div
        v-for="order in sortedOrders"
        :key="order.order_number"
        class="order-card"
        :class="{ expanded: expandedOrders.has(order.order_number) }"
      >
        <!-- Order Header (clickable) -->
        <div class="order-header" @click="toggleOrder(order.order_number)">
          <div class="order-summary">
            <span class="order-number">Order #{{ order.order_number }}</span>
            <span class="order-status" :class="getStatusClass(order.status)">
              {{ order.status }}
            </span>
          </div>
          <div class="order-meta">
            <span class="customer-info">{{ order.customer_info }}</span>
            <span class="order-date">{{ formatDate(order.placed_at) }}</span>
            <span class="expand-icon">{{ expandedOrders.has(order.order_number) ? '▲' : '▼' }}</span>
          </div>
        </div>

        <!-- Order Details (expandable) -->
        <div v-if="expandedOrders.has(order.order_number)" class="order-details">
          <div class="status-section">
            <h4>Order Status</h4>
            <div class="status-timeline">
              <div class="status-step" :class="{ active: isStatusReached(order.status, 'pending') }">
                <div class="status-dot"></div>
                <span>Pending</span>
              </div>
              <div class="status-line" :class="{ active: isStatusReached(order.status, 'preparing') }"></div>
              <div class="status-step" :class="{ active: isStatusReached(order.status, 'preparing') }">
                <div class="status-dot"></div>
                <span>Preparing</span>
              </div>
              <div class="status-line" :class="{ active: isStatusReached(order.status, 'delivering') }"></div>
              <div class="status-step" :class="{ active: isStatusReached(order.status, 'delivering') }">
                <div class="status-dot"></div>
                <span>Delivering</span>
              </div>
              <div class="status-line" :class="{ active: isStatusReached(order.status, 'delivered') }"></div>
              <div class="status-step" :class="{ active: isStatusReached(order.status, 'delivered') }">
                <div class="status-dot"></div>
                <span>Delivered</span>
              </div>
            </div>
          </div>

          <div class="info-section">
            <div class="info-row">
              <span class="info-label">Customer:</span>
              <span class="info-value">{{ order.customer_info }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Placed at:</span>
              <span class="info-value">{{ formatDateTime(order.placed_at) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">ETA Delivery:</span>
              <span class="info-value">{{ formatDateTime(order.eta_delivery) }}</span>
            </div>
            <div v-if="order.ukupno" class="info-row">
              <span class="info-label">Total:</span>
              <span class="info-value total">{{ order.ukupno }} €</span>
            </div>
          </div>

          <div class="items-section">
            <h4>Items</h4>
            <div v-if="loadingDetails.has(order.order_number)" class="loading-items">
              Loading items...
            </div>
            <ul v-else-if="orderDetails[order.order_number]?.items?.length" class="items-list">
              <li v-for="(item, idx) in orderDetails[order.order_number].items" :key="idx" class="item-row">
                <span class="item-name">{{ item.name || item.ime }}</span>
                <span class="item-quantity">x{{ item.quantity || item.kolicina }}</span>
                <span class="item-price">{{ item.price_euro || item.cijena }} €</span>
              </li>
            </ul>
            <div v-else class="no-items">No items found</div>
          </div>

          <!-- Admin Actions -->
          <div class="admin-actions">
            <h4>Update Status</h4>
            <div v-if="updatingStatus.has(order.order_number)" class="updating">
              Updating...
            </div>
            <div v-else class="action-buttons">
              <button 
                v-if="order.status === 'pending'" 
                class="btn btn-accept"
                @click.stop="updateOrderStatus(order.order_number, 'preparing')"
              >
                Accept Order
              </button>
              <button 
                v-if="order.status === 'pending'" 
                class="btn btn-reject"
                @click.stop="updateOrderStatus(order.order_number, 'rejected')"
              >
                Reject Order
              </button>
              <button 
                v-if="order.status === 'preparing'" 
                class="btn btn-next"
                @click.stop="updateOrderStatus(order.order_number, 'delivering')"
              >
                Start Delivery
              </button>
              <button 
                v-if="order.status === 'delivering'" 
                class="btn btn-complete"
                @click.stop="updateOrderStatus(order.order_number, 'delivered')"
              >
                Mark Delivered
              </button>
              <span v-if="order.status === 'delivered'" class="completed-text">
                Order completed
              </span>
              <span v-if="order.status === 'rejected'" class="rejected-text">
                Order was rejected
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="!loading" class="no-orders">No orders found.</div>
    <div v-if="loading" class="loading">Loading...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { useUserStore } from "../stores/user";
import { useRouter } from "vue-router";

const userStore = useUserStore();
const router = useRouter();
const orders = ref<any[]>([]);
const error = ref("");
const loading = ref(true);
const expandedOrders = ref<Set<string | number>>(new Set());
const orderDetails = reactive<Record<string, any>>({});
const loadingDetails = ref<Set<string | number>>(new Set());
const updatingStatus = ref<Set<string | number>>(new Set());

const statusOrder = ['pending', 'preparing', 'delivering', 'delivered'];
const statusPriority: Record<string, number> = {
  'pending': 0,
  'preparing': 1,
  'delivering': 2,
  'delivered': 3,
  'rejected': 4
};

// Sort orders: pending first, then by other statuses
const sortedOrders = computed(() => {
  return [...orders.value].sort((a, b) => {
    const priorityA = statusPriority[a.status?.toLowerCase()] ?? 99;
    const priorityB = statusPriority[b.status?.toLowerCase()] ?? 99;
    if (priorityA !== priorityB) {
      return priorityA - priorityB;
    }
    // If same status, sort by placed_at (newest first)
    return new Date(b.placed_at).getTime() - new Date(a.placed_at).getTime();
  });
});

function isStatusReached(currentStatus: string, checkStatus: string): boolean {
  const currentIndex = statusOrder.indexOf(currentStatus?.toLowerCase() || '');
  const checkIndex = statusOrder.indexOf(checkStatus);
  return currentIndex >= checkIndex;
}

function getStatusClass(status: string): string {
  const s = status?.toLowerCase() || '';
  if (s === 'delivered') return 'status-delivered';
  if (s === 'delivering') return 'status-delivering';
  if (s === 'preparing') return 'status-preparing';
  if (s === 'rejected') return 'status-rejected';
  return 'status-pending';
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString();
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleString();
}

async function toggleOrder(orderNumber: string | number) {
  if (expandedOrders.value.has(orderNumber)) {
    expandedOrders.value.delete(orderNumber);
    expandedOrders.value = new Set(expandedOrders.value);
  } else {
    expandedOrders.value.add(orderNumber);
    expandedOrders.value = new Set(expandedOrders.value);
    
    // Fetch detailed order info ako nije već učitano
    if (!orderDetails[orderNumber]) {
      await fetchOrderDetails(orderNumber);
    }
    
    // ETA provjera i auto-update statusa
    const order = orders.value.find(o => o.order_number == orderNumber);
    if (order && order.status !== 'delivered' && order.status !== 'rejected') {
      await checkAndUpdateDeliveryStatus(order);
    }
  }
}

async function checkAndUpdateDeliveryStatus(order: any) {
  if (!order.eta_delivery) return;
  
  const etaDate = new Date(order.eta_delivery);
  const now = new Date();
  
  // Ako je ETA prosla, update delivered
  if (now >= etaDate) {
    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/narudba/${order.order_number}/status`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ status: 'delivered' })
        }
      );
      if (res.ok) {
        order.status = 'delivered';
      }
    } catch (e) {
      console.error('Failed to auto-update delivery status:', e);
    }
  }
}

async function fetchOrderDetails(orderNumber: string | number) {
  loadingDetails.value.add(orderNumber);
  loadingDetails.value = new Set(loadingDetails.value);
  
  try {
    const res = await fetch(
      `${import.meta.env.VITE_API_URL}/narudba/${orderNumber}`
    );
    const data = await res.json();
    if (res.ok) {
      orderDetails[orderNumber] = data;
    }
  } catch (e) {
    console.error('Failed to fetch order details:', e);
  } finally {
    loadingDetails.value.delete(orderNumber);
    loadingDetails.value = new Set(loadingDetails.value);
  }
}

async function updateOrderStatus(orderNumber: string | number, newStatus: string) {
  updatingStatus.value.add(orderNumber);
  updatingStatus.value = new Set(updatingStatus.value);
  
  try {
    const res = await fetch(
      `${import.meta.env.VITE_API_URL}/narudba/${orderNumber}/status`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      }
    );
    const data = await res.json();
    if (res.ok) {
      // Update local order status
      const order = orders.value.find(o => o.order_number == orderNumber);
      if (order) {
        order.status = newStatus;
      }
    } else {
      error.value = data.error || 'Failed to update status';
    }
  } catch (e) {
    console.error('Failed to update order status:', e);
    error.value = 'Failed to update order status';
  } finally {
    updatingStatus.value.delete(orderNumber);
    updatingStatus.value = new Set(updatingStatus.value);
  }
}

async function fetchOrders() {
  error.value = "";
  orders.value = [];
  loading.value = true;
  
  // Check if user is admin
  if (!userStore.admin) {
    router.push('/orders');
    return;
  }
  
  try {
    const res = await fetch(
      `${import.meta.env.VITE_API_URL}/all-orders`
    );
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not fetch orders");
    orders.value = data.orders || data;
  } catch (e: any) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

onMounted(fetchOrders);
</script>

<style scoped>
.admin-orders {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  background: white;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.error-message {
  color: #dc3545;
  padding: 10px;
  background: #f8d7da;
  border-radius: 8px;
  margin-bottom: 15px;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.order-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.2s;
}

.order-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.order-card.expanded {
  border-color: #4a90d9;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  cursor: pointer;
  background: #fafafa;
  transition: background 0.2s;
}

.order-header:hover {
  background: #f0f0f0;
}

.order-summary {
  display: flex;
  align-items: center;
  gap: 12px;
}

.order-number {
  font-weight: 600;
  font-size: 1.1em;
  color: #333;
}

.order-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 500;
  text-transform: capitalize;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-preparing {
  background: #cce5ff;
  color: #004085;
}

.status-delivering {
  background: #d4edda;
  color: #155724;
}

.status-delivered {
  background: #28a745;
  color: #fff;
}

.status-rejected {
  background: #dc3545;
  color: #fff;
}

.order-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  color: #666;
}

.customer-info {
  font-weight: 500;
  color: #333;
}

.order-date {
  font-size: 0.9em;
}

.expand-icon {
  font-size: 0.8em;
  color: #999;
}

.order-details {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  background: #fff;
}

.status-section {
  margin-bottom: 20px;
}

.status-section h4,
.items-section h4,
.admin-actions h4 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 0.95em;
}

.status-timeline {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.status-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.status-step span {
  font-size: 0.75em;
  color: #999;
}

.status-step.active span {
  color: #28a745;
  font-weight: 500;
}

.status-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #e0e0e0;
  border: 2px solid #ccc;
}

.status-step.active .status-dot {
  background: #28a745;
  border-color: #28a745;
}

.status-line {
  flex: 1;
  height: 3px;
  background: #e0e0e0;
  margin: 0 5px;
  margin-bottom: 20px;
}

.status-line.active {
  background: #28a745;
}

.info-section {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-row {
  display: flex;
  gap: 8px;
}

.info-label {
  color: #666;
  font-size: 0.9em;
}

.info-value {
  font-weight: 500;
  color: #333;
  font-size: 0.9em;
}

.info-value.total {
  color: #28a745;
  font-weight: 600;
}

.items-section {
  margin-top: 15px;
}

.items-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 6px;
}

.item-name {
  flex: 1;
  font-weight: 500;
  color: #333;
}

.item-quantity {
  color: #666;
  margin: 0 15px;
}

.item-price {
  font-weight: 600;
  color: #28a745;
}

.loading-items,
.no-items {
  color: #666;
  font-style: italic;
  padding: 10px;
}

.no-orders {
  text-align: center;
  color: #666;
  padding: 40px;
}

.loading {
  text-align: center;
  color: #666;
  padding: 40px;
}

/* Admin Actions */
.admin-actions {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-accept {
  background: #28a745;
  color: #fff;
}

.btn-accept:hover {
  background: #218838;
}

.btn-reject {
  background: #dc3545;
  color: #fff;
}

.btn-reject:hover {
  background: #c82333;
}

.btn-next {
  background: #17a2b8;
  color: #fff;
}

.btn-next:hover {
  background: #138496;
}

.btn-complete {
  background: #28a745;
  color: #fff;
}

.btn-complete:hover {
  background: #218838;
}

.updating {
  color: #666;
  font-style: italic;
}

.completed-text {
  color: #28a745;
  font-weight: 500;
}

.rejected-text {
  color: #dc3545;
  font-weight: 500;
}
</style>
