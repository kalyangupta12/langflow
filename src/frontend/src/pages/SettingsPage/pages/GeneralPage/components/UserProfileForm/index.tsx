import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import IconComponent from "@/components/common/genericIconComponent";
import { Button } from "@/components/ui/button";
import { useUpdateUser } from "@/controllers/API/queries/auth";
import useAlertStore from "@/stores/alertStore";
import { checkUsernameAvailability } from "@/controllers/API/api";
import { SAVE_ERROR_ALERT, SAVE_SUCCESS_ALERT } from "@/constants/alerts_constants";

interface UserProfileFormProps {
  userData: any;
  setUserData: (data: any) => void;
}

export default function UserProfileForm({ userData, setUserData }: UserProfileFormProps) {
  const [username, setUsername] = useState(userData?.username || "");
  const [isCheckingUsername, setIsCheckingUsername] = useState(false);
  const [usernameAvailable, setUsernameAvailable] = useState<boolean | null>(null);
  const [usernameError, setUsernameError] = useState("");
  
  const setSuccessData = useAlertStore((state) => state.setSuccessData);
  const setErrorData = useAlertStore((state) => state.setErrorData);
  
  const { mutate: mutatePatchUser, isPending } = useUpdateUser();

  const originalUsername = userData?.username || "";

  useEffect(() => {
    setUsername(userData?.username || "");
  }, [userData?.username]);

  // Check username availability with debounce
  useEffect(() => {
    if (!username || username === originalUsername) {
      setUsernameAvailable(null);
      setUsernameError("");
      return;
    }

    if (username.length < 3) {
      setUsernameError("Username must be at least 3 characters");
      setUsernameAvailable(false);
      return;
    }

    const timeoutId = setTimeout(async () => {
      setIsCheckingUsername(true);
      try {
        const data = await checkUsernameAvailability(username);
        setUsernameAvailable(data.available);
        setUsernameError(data.available ? "" : "Username already taken");
      } catch (error) {
        setUsernameError("Failed to check username availability");
        setUsernameAvailable(false);
      } finally {
        setIsCheckingUsername(false);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [username, originalUsername]);

  const handleSaveUsername = () => {
    if (!usernameAvailable || username === originalUsername) {
      return;
    }

    mutatePatchUser(
      { user_id: userData!.id, user: { username } },
      {
        onSuccess: () => {
          const newUserData = { ...userData, username };
          setUserData(newUserData);
          setSuccessData({ title: SAVE_SUCCESS_ALERT });
          setUsernameAvailable(null);
        },
        onError: (error) => {
          setErrorData({
            title: SAVE_ERROR_ALERT,
            list: [(error as any)?.response?.data?.detail || "Failed to update username"],
          });
        },
      }
    );
  };

  const hasChanges = username !== originalUsername && usernameAvailable === true;

  // Display email from user data
  const displayEmail = userData?.email || userData?.username || "";

  return (
    <div className="flex w-full flex-col gap-4 rounded-md border p-4">
      <div className="flex w-full items-center justify-between">
        <div className="flex items-center gap-2">
          <IconComponent name="User" className="h-5 w-5" />
          <span className="text-lg font-semibold">Profile Information</span>
        </div>
      </div>

      <div className="flex flex-col gap-4">
        {/* Email - Read-only */}
        <div className="flex flex-col gap-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            value={displayEmail}
            disabled
            className="bg-muted cursor-not-allowed"
          />
          <span className="text-xs text-muted-foreground">
            Email cannot be changed
          </span>
        </div>

        {/* Username - Editable with availability check */}
        <div className="flex flex-col gap-2">
          <Label htmlFor="username">Username</Label>
          <div className="relative">
            <Input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={`pr-10 ${
                username !== originalUsername && usernameAvailable === false
                  ? "border-red-500"
                  : username !== originalUsername && usernameAvailable === true
                  ? "border-green-500"
                  : ""
              }`}
            />
            {isCheckingUsername && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <IconComponent name="Loader2" className="h-4 w-4 animate-spin" />
              </div>
            )}
            {!isCheckingUsername && username !== originalUsername && usernameAvailable === true && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <IconComponent name="Check" className="h-4 w-4 text-green-500" />
              </div>
            )}
            {!isCheckingUsername && username !== originalUsername && usernameAvailable === false && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <IconComponent name="X" className="h-4 w-4 text-red-500" />
              </div>
            )}
          </div>
          {usernameError && (
            <span className="text-xs text-red-500">{usernameError}</span>
          )}
          {!usernameError && username !== originalUsername && usernameAvailable === true && (
            <span className="text-xs text-green-600">Username is available</span>
          )}
        </div>

        {/* Save button */}
        {hasChanges && (
          <Button
            onClick={handleSaveUsername}
            disabled={isPending || isCheckingUsername || !usernameAvailable}
            className="w-full"
          >
            {isPending ? (
              <>
                <IconComponent name="Loader2" className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              "Save Username"
            )}
          </Button>
        )}
      </div>
    </div>
  );
}
