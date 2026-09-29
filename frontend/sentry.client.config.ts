import * as Sentry from "@sentry/nextjs";

import { config } from "@/lib/config";

Sentry.init({
  dsn: config.sentryDsn ?? undefined,
  tracesSampleRate: 1.0,
  environment: process.env.NODE_ENV || "staging",
});
