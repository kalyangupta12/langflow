import "@xyflow/react/dist/style.css";
import { Suspense, useContext, useEffect, useRef } from "react";
import { RouterProvider } from "react-router-dom";
import { AuthContext } from "./contexts/authContext";
import { LoadingPage } from "./pages/LoadingPage";
import router from "./routes";
import { useDarkStore } from "./stores/darkStore";
import { HeaderButtons } from "./components/core/folderSidebarComponent/components/sideBarFolderButtons/components/header-buttons";
export default function App() {
  const dark = useDarkStore((state) => state.dark);
  const { login, isAuthenticated } = useContext(AuthContext);
  const hasInitialized = useRef(false);
  
  useEffect(() => {
    if (!dark) {
      document.getElementById("body")!.classList.remove("dark");
    } else {
      document.getElementById("body")!.classList.add("dark");
    }
  }, [dark]);

  // Handle OAuth login - check for token in cookies or localStorage
  // Only run ONCE on initial mount
  useEffect(() => {
    // Prevent multiple initializations
    if (hasInitialized.current) {
      return;
    }
    
    // Don't auto-login if already authenticated
    if (isAuthenticated) {
      hasInitialized.current = true;
      return;
    }
    
    try {
      // First priority: Check localStorage (OAuth callback stores tokens there)
      const storedAccessToken = localStorage.getItem('access_token_lf');
      const storedRefreshToken = localStorage.getItem('refresh_token_lf');
      
      if (storedAccessToken && storedRefreshToken) {
        // Found tokens in localStorage from OAuth callback
        // Set them as cookies so they'll be sent with future requests
        document.cookie = `access_token_lf=${storedAccessToken}; path=/; max-age=86400; samesite=lax`;
        document.cookie = `refresh_token_lf=${storedRefreshToken}; path=/; max-age=604800; samesite=lax`;
        
        // Initialize auth with the access token
        login(storedAccessToken, "false");
        
        // Clean up localStorage after copying to cookies
        localStorage.removeItem('access_token_lf');
        localStorage.removeItem('refresh_token_lf');
        
        hasInitialized.current = true;
        return;
      }
      
      // Second priority: Check cookies (for returning users)
      const accessToken = document.cookie
        .split('; ')
        .find(row => row.startsWith('access_token_lf='))
        ?.split('=')[1];
      
      if (accessToken) {
        // Initialize auth with the token from cookies
        login(accessToken, "false");
      }
      
      hasInitialized.current = true;
    } catch (error) {
      console.error("Error during OAuth token handling:", error);
      hasInitialized.current = true;
    }
  }, []); // Empty dependency array - only run once on mount

  return (
    <Suspense fallback={<LoadingPage />}>
      <RouterProvider router={router} />
    </Suspense>
  );
}
