import * as SecureStore from "expo-secure-store";

export const AUTH_TOKEN_CHANGE_EVENT = "surplus-auth-token-change";

const notifyTokenChange = () => {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(AUTH_TOKEN_CHANGE_EVENT));
  }
};

export const tokenCache = {
  async getToken(key: string) {
    try {
      return await SecureStore.getItemAsync(key);
    } catch {
      if (typeof window !== "undefined" && typeof localStorage !== "undefined") {
        try {
          return localStorage.getItem(key);
        } catch {
          return null;
        }
      }
      return null;
    }
  },
  async saveToken(key: string, value: string) {
    try {
      await SecureStore.setItemAsync(key, value);
      notifyTokenChange();
      return;
    } catch {
      if (typeof window !== "undefined" && typeof localStorage !== "undefined") {
        try {
          localStorage.setItem(key, value);
          notifyTokenChange();
        } catch {
          // Ignore browser storage failures in development fallback path.
        }
      }
      return;
    }
  },
  async removeToken(key: string) {
    try {
      await SecureStore.deleteItemAsync(key);
      notifyTokenChange();
      return;
    } catch {
      if (typeof window !== "undefined" && typeof localStorage !== "undefined") {
        try {
          localStorage.removeItem(key);
          notifyTokenChange();
        } catch {
          // Ignore browser storage failures in development fallback path.
        }
      }
      return;
    }
  },
};
