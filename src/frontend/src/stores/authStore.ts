// authStore.js

import { create } from "zustand";
import {
  LANGFLOW_ACCESS_TOKEN,
  LANGFLOW_API_TOKEN,
  LANGFLOW_REFRESH_TOKEN,
} from "@/constants/constants";
import type { AuthStoreType } from "@/types/zustand/auth";
import { cookieManager, getCookiesInstance } from "@/utils/cookie-manager";

const cookies = getCookiesInstance();
const useAuthStore = create<AuthStoreType>((set, get) => ({
  isAdmin: false,
  isAuthenticated: !!cookies.get(LANGFLOW_ACCESS_TOKEN),
  accessToken: cookies.get(LANGFLOW_ACCESS_TOKEN) ?? null,
  userData: null,
  autoLogin: null,
  apiKey: cookies.get(LANGFLOW_API_TOKEN),
  authenticationErrorCount: 0,
  isLoggingOut: false, // Add flag to prevent auto-refresh during logout

  setIsAdmin: (isAdmin) => set({ isAdmin }),
  setIsAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
  setAccessToken: (accessToken) => set({ accessToken }),
  setUserData: (userData) => set({ userData }),
  setAutoLogin: (autoLogin) => set({ autoLogin }),
  setApiKey: (apiKey) => set({ apiKey }),
  setAuthenticationErrorCount: (authenticationErrorCount) =>
    set({ authenticationErrorCount }),

  logout: async () => {
    // Set logout flag to prevent token refresh
    set({ isLoggingOut: true });
    
    // Save settings that should persist across logout
    const isDark = localStorage.getItem('isDark');
    const githubStars = localStorage.getItem('githubStars');
    const githubStarsLastUpdated = localStorage.getItem('githubStarsLastUpdated');
    
    // Clear all localStorage - comprehensive cleanup
    localStorage.clear();
    
    // Restore non-auth settings
    if (isDark !== null) {
      localStorage.setItem('isDark', isDark);
    }
    if (githubStars !== null) {
      localStorage.setItem('githubStars', githubStars);
    }
    if (githubStarsLastUpdated !== null) {
      localStorage.setItem('githubStarsLastUpdated', githubStarsLastUpdated);
    }

    // Clear all session storage as well
    sessionStorage.clear();
    
    get().setIsAuthenticated(false);
    get().setIsAdmin(false);

    set({
      isAdmin: false,
      userData: null,
      accessToken: null,
      isAuthenticated: false,
      autoLogin: false,
      apiKey: null,
    });
  },
}));

export default useAuthStore;
