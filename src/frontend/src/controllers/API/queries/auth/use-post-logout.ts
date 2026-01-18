import {
  IS_AUTO_LOGIN,
  LANGFLOW_AUTO_LOGIN_OPTION,
} from "@/constants/constants";
import useAuthStore from "@/stores/authStore";
import useFlowStore from "@/stores/flowStore";
import useFlowsManagerStore from "@/stores/flowsManagerStore";
import { useFolderStore } from "@/stores/foldersStore";
import type { useMutationFunctionType } from "@/types/api";
import { getCookiesInstance } from "@/utils/cookie-manager";
import { getAuthCookie } from "@/utils/utils";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

export const useLogout: useMutationFunctionType<undefined, void> = (
  options?,
) => {
  const { mutate, queryClient } = UseRequestProcessor();
  const cookies = getCookiesInstance();
  const logout = useAuthStore((state) => state.logout);
  const isAutoLoginEnv = IS_AUTO_LOGIN;

  async function logoutUser(): Promise<any> {
    const autoLogin =
      useAuthStore.getState().autoLogin ||
      getAuthCookie(cookies, LANGFLOW_AUTO_LOGIN_OPTION) === "auto" ||
      isAutoLoginEnv;

    if (autoLogin) {
      return {};
    }
    
    // Call backend to delete server-side cookies via Set-Cookie headers
    const res = await api.post(`${getURL("LOGOUT")}`);
    return res.data;
  }

  const mutation = mutate(["useLogout"], logoutUser, {
    onSuccess: () => {
      // Backend has cleared cookies, now aggressively clear frontend
      logout();

      useFlowStore.getState().resetFlowState();
      useFlowsManagerStore.getState().resetStore();
      useFolderStore.getState().resetStore();
      queryClient.clear();
      
      // Manually delete all auth cookies with document.cookie
      const cookiesToDelete = ['access_token_lf', 'refresh_token_lf', 'apikey_tkn_lflw'];
      cookiesToDelete.forEach(name => {
        document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
        document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT; domain=${window.location.hostname}`;
        document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT; samesite=lax`;
        document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT; domain=${window.location.hostname}; samesite=lax`;
      });
      
      // Force hard reload to login page after a small delay
      setTimeout(() => {
        window.location.replace('/login');
      }, 50);
    },
    onError: (error) => {
      console.error(error);
      // Even on error, force clear everything
      logout();
      useFlowStore.getState().resetFlowState();
      useFlowsManagerStore.getState().resetStore();
      useFolderStore.getState().resetStore();
      queryClient.clear();
      
      // Clear cookies even on error
      const cookiesToDelete = ['access_token_lf', 'refresh_token_lf', 'apikey_tkn_lflw'];
      cookiesToDelete.forEach(name => {
        document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
        document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT; domain=${window.location.hostname}`;
      });
      
      setTimeout(() => {
        window.location.replace('/login');
      }, 50);
    },
    ...options,
    retry: false,
  });

  return mutation;
};
