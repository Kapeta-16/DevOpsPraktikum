import { defineStore } from "pinia";

export const useUserStore = defineStore("user", {
  state: () => ({
    username: "" as string,
    admin: false as boolean,
  }),
  actions: {
    login(username: string, admin: boolean) {
      this.username = username;
      this.admin = admin;
    },
    logout() {
      this.username = "";
      this.admin = false;
    },
  },
  persist: true,
});
