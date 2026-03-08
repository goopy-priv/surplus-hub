export const isTruthy = (value: string | undefined): boolean => {
  if (!value) return false;
  const normalized = value.trim().toLowerCase();
  return normalized === "1" || normalized === "true" || normalized === "yes" || normalized === "on";
};

type BypassAuthOptions = {
  nodeEnv?: string;
  devBypassFlag?: string;
};

export const shouldBypassAuth = ({
  nodeEnv = process.env.NODE_ENV,
  devBypassFlag = process.env.NEXT_PUBLIC_DEV_AUTH_BYPASS,
}: BypassAuthOptions = {}): boolean => {
  return nodeEnv === "test" || isTruthy(devBypassFlag);
};

export const hasStoredAuthToken = (storage?: Pick<Storage, "getItem"> | null): boolean => {
  const targetStorage =
    storage ?? (typeof window !== "undefined" && typeof localStorage !== "undefined" ? localStorage : null);

  if (!targetStorage) {
    return false;
  }

  try {
    return Boolean(targetStorage.getItem("access_token") || targetStorage.getItem("clerk_token"));
  } catch {
    return false;
  }
};
