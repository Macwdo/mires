# Root layout

The root remains a Server Component and owns document metadata and global CSS.

<!-- artifact: src/app/layout.tsx; profiles: base,forms,data,auth,realtime,full -->
```tsx
import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Frontend Standards",
    template: "%s | Frontend Standards",
  },
  description: "Executable React and Next.js production standards.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main">
          Skip to content
        </a>
        {children}
      </body>
    </html>
  );
}
```
