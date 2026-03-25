import { ClerkProvider, SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'
import { Providers } from "./providers";
import "./globals.css";
import Link from 'next/link';
import { ServiceWorkerUnregister } from './sw-unregister';
import { BottomNav } from '../components/BottomNav';
import { DesktopNav } from "../components/DesktopNav";

import type { Metadata } from 'next';

const CLERK_PUBLISHABLE_KEY = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ?? "";
if (!CLERK_PUBLISHABLE_KEY && process.env.NODE_ENV === "production") {
  throw new Error("Missing NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY environment variable");
}

export const metadata: Metadata = {
  title: "잉여자재 - B2B 잉여자재 거래",
  description: "내 근처 잉여자재를 찾아보세요. 공장/건설 잉여자재 B2B 거래 플랫폼.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
      <html lang="en">
        <body>
          <Providers>
            <ServiceWorkerUnregister />
            <header className="px-4 py-3 border-b border-border flex justify-between items-center bg-card shadow-sm sticky top-0 z-50">
              <div className="flex items-center gap-2">
                <div className="bg-gradient-to-br from-primary to-primary-dark p-2 rounded-[10px] w-9 h-9 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 text-white">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
                  </svg>
                </div>
                <Link href="/" className="text-xl font-bold text-foreground">잉여자재</Link>
              </div>

              <div className="hidden md:flex flex-1 max-w-md mx-8">
                <div className="relative w-full">
                  <input
                    type="search"
                    placeholder="자재, 공구, 설비 검색"
                    className="w-full rounded-full bg-secondary border border-border px-4 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
                  />
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none">
                    <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                  </svg>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <DesktopNav />
                <div className="flex items-center gap-4">
                  <SignedOut>
                    <SignInButton>
                      <button className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">로그인</button>
                    </SignInButton>
                  </SignedOut>
                  <SignedIn>
                    <UserButton afterSignOutUrl="/" />
                  </SignedIn>
                </div>
              </div>
            </header>
            <main className="min-h-screen bg-background pb-24 md:pb-8">{children}</main>
            <BottomNav />
          </Providers>
        </body>
      </html>
    </ClerkProvider>
  )
}
