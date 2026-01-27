import { createRouter, createWebHistory } from "vue-router";
import Menu from "../views/Menu.vue";
import Login from "../views/Login.vue";
import UserOrders from "../views/UserOrders.vue";
const routes = [
  { path: "/", name: "Menu", component: Menu },
  { path: "/login", name: "Login", component: Login },
  { path: "/orders", name: "Orders", component: UserOrders },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
