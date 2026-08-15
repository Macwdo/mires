# Example route

The route composes server-rendered content with one narrow interactive island.
No business rule lives in the route.

<!-- artifact: src/app/page.tsx; profiles: base,forms,data,auth,realtime -->
```tsx
import Link from "next/link";

import { ReferenceTabs } from "@/features/home/reference-tabs";

export default function Page() {
  return (
    <main id="main" className="shell">
      <p className="eyebrow">Production reference</p>
      <h1>React and Next.js standards</h1>
      <p className="lede">
        Server-rendered by default, interactive only where the interface requires it.
      </p>

      <ReferenceTabs />

      <Link href="/error-demo">Open the recoverable error example</Link>
    </main>
  );
}
```

<!-- artifact: src/app/page.tsx; profiles: full -->
```tsx
import Link from "next/link";

import { ReferenceTabs } from "@/features/home/reference-tabs";

export default function Page() {
  return (
    <main id="main" className="shell">
      <p className="eyebrow">Production reference</p>
      <h1>React and Next.js standards</h1>
      <p className="lede">
        Server-rendered by default, with small client islands for real interaction.
      </p>

      <ReferenceTabs />

      <nav aria-label="Examples" className="links">
        <Link href="/protected">Protected route</Link>
        <Link href="/error-demo">Recoverable error</Link>
      </nav>
    </main>
  );
}
```

<!-- artifact: src/features/home/reference-tabs.tsx; profiles: base,forms,data,auth,realtime -->
```tsx
"use client";

import { Tabs } from "@/components/ui/tabs";

export function ReferenceTabs() {
  return (
    <Tabs.Root defaultValue="architecture" aria-label="Reference topics">
      <Tabs.List>
        <Tabs.Tab value="architecture">Architecture</Tabs.Tab>
        <Tabs.Tab value="quality">Quality</Tabs.Tab>
      </Tabs.List>
      <Tabs.Panel value="architecture">
        Keep routes thin, validate boundaries, and organize behavior by feature.
      </Tabs.Panel>
      <Tabs.Panel value="quality">
        Accessibility, security, and explicit states are release criteria.
      </Tabs.Panel>
    </Tabs.Root>
  );
}
```

<!-- artifact: src/features/home/reference-tabs.tsx; profiles: full -->
```tsx
"use client";

import { Tabs } from "@/components/ui/tabs";
import { ContactForm } from "@/features/forms/contact-form";
import { ProductsPanel } from "@/features/products/products-panel";
import { QueryProvider } from "@/features/products/query-provider";
import { RealtimeStatus } from "@/features/realtime/realtime-status";

export function ReferenceTabs() {
  return (
    <Tabs.Root defaultValue="forms" aria-label="Executable recipes">
      <Tabs.List>
        <Tabs.Tab value="forms">Forms</Tabs.Tab>
        <Tabs.Tab value="data">Data</Tabs.Tab>
        <Tabs.Tab value="realtime">Realtime</Tabs.Tab>
      </Tabs.List>
      <Tabs.Panel value="forms">
        <ContactForm />
      </Tabs.Panel>
      <Tabs.Panel value="data">
        <QueryProvider>
          <ProductsPanel />
        </QueryProvider>
      </Tabs.Panel>
      <Tabs.Panel value="realtime">
        <RealtimeStatus />
      </Tabs.Panel>
    </Tabs.Root>
  );
}
```
