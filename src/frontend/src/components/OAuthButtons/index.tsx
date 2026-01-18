import { useContext, useState } from "react";
import GoogleIcon from "@/assets/google-icon.svg?react";
import PhantomIcon from "@/assets/phantom-icon.svg?react";
import { Button } from "@/components/ui/button";
import { AuthContext } from "@/contexts/authContext";
import useAlertStore from "@/stores/alertStore";
import { useQueryClient } from "@tanstack/react-query";

interface OAuthButtonsProps {
  className?: string;
}

export default function OAuthButtons({ className }: OAuthButtonsProps) {
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isPhantomLoading, setIsPhantomLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const setErrorData = useAlertStore((state) => state.setErrorData);
  const queryClient = useQueryClient();

  const handleGoogleLogin = async () => {
    setIsGoogleLoading(true);
    try {
      // Get authorization URL from backend
      const response = await fetch("/api/v1/oauth/google/authorize");
      
      if (!response || !response.ok) {
        const errorData = response ? await response.json() : { detail: "No response from server" };
        throw new Error(errorData.detail || "Google OAuth is not configured");
      }
      
      const data = await response.json();
      
      if (data && data.authorization_url) {
        // Redirect to Google OAuth consent screen
        window.location.href = data.authorization_url;
      } else {
        throw new Error("Failed to get Google authorization URL");
      }
    } catch (error) {
      setIsGoogleLoading(false);
      
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      const isConfigError = errorMessage.includes("not configured");
      
      setErrorData({
        title: "Google Sign-In Not Available",
        list: [
          isConfigError
            ? "Google OAuth is not configured by the administrator. Please use username/password login or try Phantom wallet."
            : errorMessage
        ],
      });
    }
  };

  const handlePhantomLogin = async () => {
    setIsPhantomLoading(true);
    
    try {
      // Check if Phantom is installed
      const phantom = (window as any).phantom?.solana;
      
      if (!phantom) {
        window.open("https://phantom.app/", "_blank");
        setErrorData({
          title: "Phantom Wallet Not Found",
          list: [
            "Please install Phantom wallet extension and refresh the page."
          ],
        });
        setIsPhantomLoading(false);
        return;
      }

      // Connect to Phantom wallet
      const resp = await phantom.connect();
      const publicKey = resp.publicKey.toString();

      // Get message to sign from backend
      const messageResponse = await fetch("/api/v1/oauth/phantom/message");
      const { message, nonce } = await messageResponse.json();

      // Encode message
      const encodedMessage = new TextEncoder().encode(message);
      
      // Request signature
      const signedMessage = await phantom.signMessage(encodedMessage, "utf8");
      
      // Verify signature with backend
      const verifyResponse = await fetch("/api/v1/oauth/phantom/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          publicKey: publicKey,
          signature: Array.from(signedMessage.signature),
          message: message,
        }),
      });

      if (!verifyResponse.ok) {
        throw new Error("Failed to verify wallet signature");
      }

      const tokens = await verifyResponse.json();
      
      // Login with received tokens
      login(tokens.access_token, "phantom", tokens.refresh_token);
      queryClient.clear();
      
    } catch (error) {
      setIsPhantomLoading(false);
      setErrorData({
        title: "Phantom Sign-In Error",
        list: [
          error instanceof Error 
            ? error.message 
            : "Failed to sign in with Phantom wallet."
        ],
      });
    }
  };

  return (
    <div className={`flex flex-col gap-3 w-full ${className || ""}`}>
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-muted px-2 text-muted-foreground">
            Or continue with
          </span>
        </div>
      </div>
      
      <Button
        type="button"
        variant="outline"
        className="w-full"
        onClick={handleGoogleLogin}
        disabled={isGoogleLoading}
      >
        {isGoogleLoading ? (
          <span className="flex items-center gap-2">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            Connecting...
          </span>
        ) : (
          <span className="flex items-center gap-2">
            <GoogleIcon className="h-5 w-5" />
            Sign in with Google
          </span>
        )}
      </Button>

      <Button
        type="button"
        variant="outline"
        className="w-full"
        onClick={handlePhantomLogin}
        disabled={isPhantomLoading}
      >
        {isPhantomLoading ? (
          <span className="flex items-center gap-2">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            Connecting...
          </span>
        ) : (
          <span className="flex items-center gap-2">
            <PhantomIcon className="h-5 w-5" />
            Sign in with Phantom
          </span>
        )}
      </Button>
    </div>
  );
}
