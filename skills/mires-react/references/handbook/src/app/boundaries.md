# Route boundaries

Error recovery is interactive, so the error boundary is a Client Component.
The not-found boundary stays server-rendered.

<!-- artifact: src/app/error.tsx; profiles: base,forms,data,auth,realtime,full -->
```tsx
"use client";

import { useEffect, useRef } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const retryRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    console.error("Route rendering failed", { digest: error.digest });
    retryRef.current?.focus();
  }, [error]);

  return (
    <main id="main" className="shell">
      <h1>Something went wrong</h1>
      <p role="alert">The page could not be displayed. Try the operation again.</p>
      <button ref={retryRef} className="button" type="button" onClick={reset}>
        Try again
      </button>
    </main>
  );
}
```

<!-- artifact: src/app/not-found.tsx; profiles: base,forms,data,auth,realtime,full -->
```tsx
import Link from "next/link";

export default function NotFound() {
  return (
    <main id="main" className="shell">
      <h1>Page not found</h1>
      <p>The requested page does not exist or is no longer available.</p>
      <Link href="/">Return home</Link>
    </main>
  );
}
```

<!-- artifact: src/app/loading.tsx; profiles: base,forms,data,auth,realtime,full -->
```tsx
export default function Loading() {
  return (
    <main id="main" className="shell" aria-busy="true" aria-live="polite">
      <p>Loading page…</p>
    </main>
  );
}
```

<!-- artifact: src/app/error-demo/page.tsx; profiles: base,forms,data,auth,realtime,full -->
```tsx
"use client";

import { useState } from "react";

export default function ErrorDemoPage() {
  const [shouldFail, setShouldFail] = useState(false);

  if (shouldFail) {
    throw new Error("Deterministic demonstration error");
  }

  return (
    <main id="main" className="shell">
      <h1>Recoverable error</h1>
      <button className="button" type="button" onClick={() => setShouldFail(true)}>
        Trigger error
      </button>
    </main>
  );
}
```
