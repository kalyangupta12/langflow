import "@xyflow/react/dist/style.css";
import { Suspense, useContext, useEffect } from "react";
import { RouterProvider } from "react-router-dom";
import { AuthContext } from "./contexts/authContext";
import { LoadingPage } from "./pages/LoadingPage";
import router from "./routes";
import { useDarkStore } from "./stores/darkStore";

export default function App() {
  const dark = useDarkStore((state) => state.dark);
  const { login } = useContext(AuthContext);
  
  useEffect(() => {
    if (!dark) {
      document.getElementById("body")!.classList.remove("dark");
    } else {
      document.getElementById("body")!.classList.add("dark");
    }
  }, [dark]);

  // Handle OAuth redirect with access token
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get("access_token");
    
    if (accessToken) {
      // Use the login function to properly store the token
      login(accessToken, "false");
      // Clean up URL and redirect to home
      window.history.replaceState({}, document.title, "/");
      window.location.href = "/";
    }
  }, [login]);

  return (
    <Suspense fallback={<LoadingPage />}>
      <RouterProvider router={router} />
    </Suspense>
  );
}
