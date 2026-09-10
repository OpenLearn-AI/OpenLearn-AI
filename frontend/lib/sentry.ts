import * as Sentry from "@sentry/nextjs";

export function initSentry() {
  if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
    Sentry.init({
      dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
      
    
      tracesSampleRate: 1.0, 
      
   
      environment: process.env.NODE_ENV || "staging", 
    });
  } else {
    console.warn("Sentry DSN is not defined in environment variables.");
  }
}