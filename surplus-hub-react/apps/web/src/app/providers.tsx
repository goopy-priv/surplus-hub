"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { configureApiClient } from "@repo/core";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "production" ? "" : "http://localhost:8000");


configureApiClient({
  baseUrl: API_BASE_URL,
  tokenProvider: async () => {
    try {
      // Access the global Clerk instance injected by ClerkProvider
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const clerk = (window as any).Clerk;
      if (clerk && clerk.session) {
        return await clerk.session.getToken();
      }
    } catch {
      // Ignore errors when accessing window or Clerk
    }
    return null;
  },
});


type ProvidersProps = {
  children?: unknown;
};

export function Providers({ children }: ProvidersProps) {
  const [queryClient] = useState(() => new QueryClient());

  return (
    // Workspace currently installs multiple React type versions; cast keeps app typing unblocked.
    <QueryClientProvider client={queryClient}>{children as any}</QueryClientProvider>
  );
}
