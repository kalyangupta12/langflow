import { useContext, useState } from "react";
import GoogleIcon from "@/assets/google-icon.svg?react";
import PhantomIcon from "@/assets/phantom-icon.svg?react";
import { Button } from "@/components/ui/button";
import { AuthContext } from "@/contexts/authContext";
import useAlertStore from "@/stores/alertStore";
import { useQueryClient } from "@tanstack/react-query";
import { Wallet } from "lucide-react";
import Solflare from "@/assets/solflare.svg?react";
import BackpackIcon from "@/assets/backpack.svg?react";
interface OAuthButtonsProps {
  className?: string;
}

export default function OAuthButtons({ className }: OAuthButtonsProps) {
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isPhantomLoading, setIsPhantomLoading] = useState(false);
  const [isSolflareLoading, setIsSolflareLoading] = useState(false);
  const [isBackpackLoading, setIsBackpackLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const setErrorData = useAlertStore((state) => state.setErrorData);
  const queryClient = useQueryClient();

  const handleGoogleLogin = async () => {
    setIsGoogleLoading(true);
    try {
      // Get authorization URL from backend
      const response = await fetch("/api/v1/oauth/google/authorize").catch(err => {
        throw new Error("Cannot connect to server. Please check if backend is running.");
      });
      
      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { detail: "Google OAuth is not configured" };
        }
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
        // window.open("https://phantom.app/", "_blank");
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
      const messageResponse = await fetch("/api/v1/oauth/phantom/message").catch(err => {
        throw new Error("Cannot connect to server. Please check if backend is running.");
      });
      
      if (!messageResponse.ok) {
        throw new Error("Failed to get signature message from server");
      }
      
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
          provider: "phantom",
        }),
      }).catch(err => {
        throw new Error("Cannot connect to server. Please check if backend is running.");
      });

      if (!verifyResponse.ok) {
        let errorDetail;
        try {
          const errorData = await verifyResponse.json();
          errorDetail = errorData.detail || "Failed to verify wallet signature";
        } catch {
          errorDetail = "Failed to verify wallet signature";
        }
        throw new Error(errorDetail);
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

  const handleSolflareLogin = async () => {
    setIsSolflareLoading(true);
    
    try {
      // Check if Solflare is installed
      const solflare = (window as any).solflare;
      
      if (!solflare || !solflare.isSolflare) {
        // window.open("https://solflare.com/", "_blank");
        setErrorData({
          title: "Solflare Wallet Not Found",
          list: [
            "Please install Solflare wallet extension and refresh the page."
          ],
        });
        setIsSolflareLoading(false);
        return;
      }

      // Connect to Solflare wallet
      await solflare.connect();
      const publicKey = solflare.publicKey.toString();

      // Get message to sign from backend
      const messageResponse = await fetch("/api/v1/oauth/phantom/message").catch(err => {
        throw new Error("Cannot connect to server. Please check if backend is running.");
      });
      
      if (!messageResponse.ok) {
        throw new Error("Failed to get signature message from server");
      }
      
      const { message } = await messageResponse.json();

      // Encode message
      const encodedMessage = new TextEncoder().encode(message);
      
      // Request signature
      const signedMessage = await solflare.signMessage(encodedMessage, "utf8");
      
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
          provider: "solflare",
        }),
      }).catch(err => {
        throw new Error("Cannot connect to server. Please check if backend is running.");
      });

      if (!verifyResponse.ok) {
        let errorDetail;
        try {
          const errorData = await verifyResponse.json();
          errorDetail = errorData.detail || "Failed to verify wallet signature";
        } catch {
          errorDetail = "Failed to verify wallet signature";
        }
        throw new Error(errorDetail);
      }

      const tokens = await verifyResponse.json();
      
      // Login with received tokens
      login(tokens.access_token, "solflare", tokens.refresh_token);
      queryClient.clear();
      
    } catch (error) {
      setIsSolflareLoading(false);
      setErrorData({
        title: "Solflare Sign-In Error",
        list: [
          error instanceof Error 
            ? error.message 
            : "Failed to sign in with Solflare wallet."
        ],
      });
    }
  };

  const handleBackpackLogin = async () => {
    setIsBackpackLoading(true);
    
    try {
      // Check if Backpack is installed - Backpack uses window.backpack or window.xnft
      const backpack = (window as any).backpack || (window as any).xnft?.solana;
      
      if (!backpack) {
        window.open("https://backpack.app/", "_blank");
        setErrorData({
          title: "Backpack Wallet Not Found",
          list: [
            "Please install Backpack wallet extension and refresh the page."
          ],
        });
        setIsBackpackLoading(false);
        return;
      }

      // Connect to Backpack wallet
      const response = await backpack.connect();
      
      // Backpack may return publicKey in different ways
      let publicKey: string;
      if (response?.publicKey) {
        publicKey = typeof response.publicKey === 'string' 
          ? response.publicKey 
          : response.publicKey.toString();
      } else if (backpack.publicKey) {
        publicKey = typeof backpack.publicKey === 'string'
          ? backpack.publicKey
          : backpack.publicKey.toString();
      } else {
        throw new Error("Failed to get public key from Backpack wallet");
      }

      // Get message to sign from backend
      const messageResponse = await fetch("/api/v1/oauth/phantom/message").catch(err => {
        throw new Error("Cannot connect to server. Please check if backend is running.");
      });
      
      if (!messageResponse.ok) {
        throw new Error("Failed to get signature message from server");
      }
      
      const { message } = await messageResponse.json();

      // Encode message
      const encodedMessage = new TextEncoder().encode(message);
      
      // Request signature - Backpack uses signMessage
      const signedMessage = await backpack.signMessage(encodedMessage);
      
      // Backpack may return signature in different formats
      let signatureArray: number[];
      if (signedMessage.signature) {
        signatureArray = Array.isArray(signedMessage.signature) 
          ? signedMessage.signature 
          : Array.from(signedMessage.signature);
      } else if (Array.isArray(signedMessage)) {
        signatureArray = signedMessage;
      } else if (signedMessage instanceof Uint8Array) {
        signatureArray = Array.from(signedMessage);
      } else {
        throw new Error("Invalid signature format from Backpack wallet");
      }
      
      // Verify signature with backend
      const verifyResponse = await fetch("/api/v1/oauth/phantom/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          publicKey: publicKey,
          signature: signatureArray,
          message: message,
          provider: "backpack",
        }),
      }).catch(err => {
        throw new Error("Cannot connect to server. Please check if backend is running.");
      });

      if (!verifyResponse.ok) {
        let errorDetail;
        try {
          const errorData = await verifyResponse.json();
          errorDetail = errorData.detail || "Failed to verify wallet signature";
        } catch {
          errorDetail = "Failed to verify wallet signature";
        }
        throw new Error(errorDetail);
      }

      const tokens = await verifyResponse.json();
      
      // Login with received tokens
      login(tokens.access_token, "backpack", tokens.refresh_token);
      queryClient.clear();
      
    } catch (error) {
      setIsBackpackLoading(false);
      setErrorData({
        title: "Backpack Sign-In Error",
        list: [
          error instanceof Error 
            ? error.message 
            : "Failed to sign in with Backpack wallet."
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

      <Button
        type="button"
        variant="outline"
        className="w-full"
        onClick={handleSolflareLogin}
        disabled={isSolflareLoading}
      >
        {isSolflareLoading ? (
          <span className="flex items-center gap-2">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            Connecting...
          </span>
        ) : (
          <span className="flex items-center gap-2">
            <Solflare className="h-5 w-5" />
            Sign in with Solflare
          </span>
        )}
      </Button>

      <Button
        type="button"
        variant="outline"
        className="w-full"
        onClick={handleBackpackLogin}
        disabled={isBackpackLoading}
      >
        {isBackpackLoading ? (
          <span className="flex items-center gap-2">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            Connecting...
          </span>
        ) : (
          <span className="flex items-center gap-2">
            <BackpackIcon className="h-5 w-5" />
            Sign in with Backpack
          </span>
        )}
      </Button>
    </div>
  );
}
