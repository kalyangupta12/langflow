import * as Form from "@radix-ui/react-form";
import { type FormEvent, useEffect, useState } from "react";
import AgentsTrail from "@/assets/AgentsTrail.svg?react";
// import Antigravity from "@/components/Antigravity";
import Galaxy from "@/components/Galaxy/Galaxy";
import InputComponent from "@/components/core/parameterRenderComponent/components/inputComponent";
import OAuthButtons from "@/components/OAuthButtons";
import { useAddUser } from "@/controllers/API/queries/auth";
import { CustomLink } from "@/customization/components/custom-link";
import { useCustomNavigate } from "@/customization/hooks/use-custom-navigate";
import { track } from "@/customization/utils/analytics";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { SIGNUP_ERROR_ALERT } from "../../constants/alerts_constants";
import {
  CONTROL_INPUT_STATE,
  SIGN_UP_SUCCESS,
} from "../../constants/constants";
import useAlertStore from "../../stores/alertStore";
import type {
  inputHandlerEventType,
  signUpInputStateType,
  UserInputType,
} from "../../types/components";
import MetallicPaint, {parseLogoImage} from "@/components/MettalicPaint/MetallicPaint";

export default function SignUp(): JSX.Element {
  const [inputState, setInputState] =
    useState<signUpInputStateType>(CONTROL_INPUT_STATE);

  const [isDisabled, setDisableBtn] = useState<boolean>(true);

  const { password, cnfPassword, username } = inputState;
  const setSuccessData = useAlertStore((state) => state.setSuccessData);
  const setErrorData = useAlertStore((state) => state.setErrorData);
  const navigate = useCustomNavigate();

  const { mutate: mutateAddUser } = useAddUser();

  function handleInput({
    target: { name, value },
  }: inputHandlerEventType): void {
    setInputState((prev) => ({ ...prev, [name]: value }));
  }

  useEffect(() => {
    if (password !== cnfPassword) return setDisableBtn(true);
    if (password === "" || cnfPassword === "") return setDisableBtn(true);
    if (username === "") return setDisableBtn(true);
    setDisableBtn(false);
  }, [password, cnfPassword, username, handleInput]);

  function handleSignup(): void {
    const { username, password } = inputState;
    const newUser: UserInputType = {
      username: username.trim(),
      password: password.trim(),
    };

    mutateAddUser(newUser, {
      onSuccess: (user) => {
        track("User Signed Up", user);
        setSuccessData({
          title: SIGN_UP_SUCCESS,
        });
        navigate("/login");
      },
      onError: (error) => {
        const {
          response: {
            data: { detail },
          },
        } = error;
        setErrorData({
          title: SIGNUP_ERROR_ALERT,
          list: [detail],
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
                  <h1 className="text-5xl pb-1 font-bold bg-gradient-to-r from-gray-400 via-gray-100 to-gray-400 bg-clip-text text-transparent">
                  AgentsTrail AI
                  </h1>
                <p className="text-xl text-muted-foreground">
                  Where AI Agents Meet Web3
                </p>
              </div>
            </div>

      {/* Right Side - Sign Up Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center bg-background p-8">
        <Form.Root
          onSubmit={(event: FormEvent<HTMLFormElement>) => {
            if (password === "") {
              event.preventDefault();
              return;
            }

            const _data = Object.fromEntries(new FormData(event.currentTarget));
            event.preventDefault();
          }}
          className="w-full max-w-md space-y-6"
        >
          <div className="space-y-2 text-center">
            <h2 className="text-3xl font-bold text-foreground">Sign up <span className="text-primary">for</span> AgentsTrail AI</h2>
            <p className="text-sm text-muted-foreground">
              Create an account and start making agents today!
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
              <Form.Field name="password" serverInvalid={password != cnfPassword}>
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
                  Please enter a password
                </Form.Message>
                {password != cnfPassword && (
                  <Form.Message className="field-invalid text-xs">
                    Passwords do not match
                  </Form.Message>
                )}
              </Form.Field>
            </div>

            <div className="space-y-2">
              <Form.Field
                name="confirmpassword"
                serverInvalid={password != cnfPassword}
              >
                <Form.Label className="data-[invalid]:label-invalid text-sm font-medium">
                  Confirm Password <span className="text-destructive">*</span>
                </Form.Label>
                <InputComponent
                  onChange={(value) => {
                    handleInput({ target: { name: "cnfPassword", value } });
                  }}
                  value={cnfPassword}
                  isForm
                  password={true}
                  required
                  placeholder="Confirm your password"
                  className="w-full"
                />
                <Form.Message className="field-invalid text-xs" match="valueMissing">
                  Please confirm your password
                </Form.Message>
              </Form.Field>
            </div>

            <Form.Submit asChild>
              <Button
                disabled={isDisabled}
                type="submit"
                className="w-full"
                size="lg"
                onClick={() => {
                  handleSignup();
                }}
              >
                Sign up
              </Button>
            </Form.Submit>
          </div>

          <OAuthButtons />

          <div className="text-center">
            <CustomLink to="/login">
              <Button className="w-full" variant="outline">
                Already have an account?&nbsp;<b>Sign in</b>
              </Button>
            </CustomLink>
          </div>
        </Form.Root>
      </div>
    </div>
  );
}
