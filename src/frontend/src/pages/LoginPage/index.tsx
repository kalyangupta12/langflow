import * as Form from "@radix-ui/react-form";
import { useQueryClient } from "@tanstack/react-query";
import { useContext, useState } from "react";
import AgentsTrail from "@/assets/AgentsTrail.svg?react";
// import Antigravity from "@/components/Antigravity";
import OAuthButtons from "@/components/OAuthButtons";
import Galaxy from "@/components/Galaxy/Galaxy";
import { useLoginUser } from "@/controllers/API/queries/auth";
import { CustomLink } from "@/customization/components/custom-link";
import { useSanitizeRedirectUrl } from "@/hooks/use-sanitize-redirect-url";
import InputComponent from "../../components/core/parameterRenderComponent/components/inputComponent";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { SIGNIN_ERROR_ALERT } from "../../constants/alerts_constants";
import { CONTROL_LOGIN_STATE, IS_AUTO_LOGIN } from "../../constants/constants";
import { AuthContext } from "../../contexts/authContext";
import useAlertStore from "../../stores/alertStore";
import type { LoginType } from "../../types/api";
import type {
  inputHandlerEventType,
  loginInputStateType,
} from "../../types/components";

export default function LoginPage(): JSX.Element {
  const [inputState, setInputState] =
    useState<loginInputStateType>(CONTROL_LOGIN_STATE);

  const { password, username } = inputState;

  useSanitizeRedirectUrl();

  const { login, clearAuthSession } = useContext(AuthContext);
  const setErrorData = useAlertStore((state) => state.setErrorData);

  function handleInput({
    target: { name, value },
  }: inputHandlerEventType): void {
    setInputState((prev) => ({ ...prev, [name]: value }));
  }

  const { mutate } = useLoginUser();
  const queryClient = useQueryClient();

  function signIn() {
    const user: LoginType = {
      username: username.trim(),
      password: password.trim(),
    };

    mutate(user, {
      onSuccess: (data) => {
        clearAuthSession();
        login(data.access_token, "login", data.refresh_token);
        queryClient.clear();
      },
      onError: (error) => {
        setErrorData({
          title: SIGNIN_ERROR_ALERT,
          list: [error["response"]["data"]["detail"]],
        });
      },
    });
  }

  return (
    <div className="flex h-screen w-full overflow-hidden">
      {/* Left Side - Antigravity Animation */}
      <div className="hidden lg:flex lg:w-1/2 bg-black relative items-center justify-center p-12">
        <div className="absolute inset-0">
          {/* <Antigravity
            count={300}
            magnetRadius={6}
            ringRadius={7}
            waveSpeed={0.4}
            waveAmplitude={1}
            particleSize={1.5}
            lerpSpeed={0.05}
            color="#c8c3da"
            autoAnimate
            particleVariance={1}
            rotationSpeed={0}
            depthFactor={1}
            pulseSpeed={3}
            particleShape="capsule"
            fieldStrength={10}
          /> */}
          <Galaxy 
    mouseRepulsion
    mouseInteraction
    density={1}
    glowIntensity={0.3}
    saturation={0}
    hueShift={140}
    twinkleIntensity={0.3}
    rotationSpeed={0.1}
    repulsionStrength={2}
    autoCenterRepulsion={0}
    starSpeed={0.5}
    speed={1}
/>
        </div>
        <div className="relative z-10 space-y-6 text-center">
          <div className="h-28 w-28 mx-auto relative p-2" style={{ 
            filter: 'drop-shadow(0 0 20px rgba(255,255,255,0.3))',
            overflow: 'visible'
          }}>
            <AgentsTrail 
              className="h-full w-full" 
              style={{ 
                fill: 'url(#metallic-gradient)',
                filter: 'contrast(1.2) brightness(1.1)',
                overflow: 'visible'
              }} 
            />
            <svg width="0" height="0" style={{ position: 'absolute' }}>
              <defs>
                <linearGradient id="metallic-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#E8E8E8', stopOpacity: 1 }} />
                  <stop offset="25%" style={{ stopColor: '#FFFFFF', stopOpacity: 1 }} />
                  <stop offset="50%" style={{ stopColor: '#C0C0C0', stopOpacity: 1 }} />
                  <stop offset="75%" style={{ stopColor: '#FFFFFF', stopOpacity: 1 }} />
                  <stop offset="100%" style={{ stopColor: '#D0D0D0', stopOpacity: 1 }} />
                </linearGradient>
              </defs>
            </svg>
          </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-400 via-gray-100 to-gray-400 bg-clip-text text-transparent pb-1">
            AgentsTrail AI
            </h1>
          <p className="text-xl text-muted-foreground">
            Where AI Agents Meet Web3
          </p>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center bg-background p-8">
        <Form.Root
          onSubmit={(event) => {
            if (password === "") {
              event.preventDefault();
              return;
            }
            signIn();
            const _data = Object.fromEntries(new FormData(event.currentTarget));
            event.preventDefault();
          }}
          className="w-full max-w-md space-y-6"
        >
          <div className="space-y-2 text-center">
            <h2 className="text-3xl font-bold text-foreground">Log in <span className="text-primary">or</span> sign in</h2>
            <p className="text-sm text-muted-foreground">
              Log in and start making agents today!
            </p>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <Form.Field name="username">
                <Form.Label className="data-[invalid]:label-invalid text-sm font-medium">
                  Username <span className="text-destructive">*</span>
                </Form.Label>
                <Form.Control asChild>
                  <Input
                    type="username"
                    onChange={({ target: { value } }) => {
                      handleInput({ target: { name: "username", value } });
                    }}
                    value={username}
                    className="w-full"
                    required
                    placeholder="Username"
                  />
                </Form.Control>
                <Form.Message match="valueMissing" className="field-invalid text-xs">
                  Please enter your username
                </Form.Message>
              </Form.Field>
            </div>

            <div className="space-y-2">
              <Form.Field name="password">
                <Form.Label className="data-[invalid]:label-invalid text-sm font-medium">
                  Password <span className="text-destructive">*</span>
                </Form.Label>
                <InputComponent
                  onChange={(value) => {
                    handleInput({ target: { name: "password", value } });
                  }}
                  value={password}
                  isForm
                  password={true}
                  required
                  placeholder="Password"
                  className="w-full"
                />
                <Form.Message className="field-invalid text-xs" match="valueMissing">
                  Please enter your password
                </Form.Message>
              </Form.Field>
            </div>

            <Form.Submit asChild>
              <Button className="w-full" type="submit" size="lg">
                Sign in
              </Button>
            </Form.Submit>
          </div>

          <OAuthButtons />

          <div className="text-center">
            <CustomLink to="/signup">
              <Button className="w-full" variant="outline" type="button">
                Don't have an account?&nbsp;<b>Sign Up</b>
              </Button>
            </CustomLink>
          </div>
        </Form.Root>
      </div>
    </div>
  );
}
