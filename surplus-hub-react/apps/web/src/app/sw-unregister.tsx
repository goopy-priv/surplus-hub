"use client";

import { useEffect } from 'react';

export function ServiceWorkerUnregister() {
  useEffect(() => {
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistrations().then(function(registrations) {
        for(let registration of registrations) {
          console.log('Unregistering Service Worker:', registration);
          registration.unregister();
        }
      });
    }
  }, []);
  return null;
}
