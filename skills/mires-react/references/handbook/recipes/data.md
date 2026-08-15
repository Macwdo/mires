# Typed API and client server-state recipe

Fetch in Server Components unless the user experience genuinely needs
client-side cache coordination. This example justifies TanStack Query with
retry and a mutation that invalidates a shared list. Every response is parsed
as untrusted input. Filters and pagination remain in the URL.

<!-- artifact: src/lib/api-client.ts; profiles: data,full -->
```ts
import type { ZodType } from "zod";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function requestJson<T>(
  input: RequestInfo | URL,
  schema: ZodType<T>,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(input, {
    ...init,
    headers: {
      Accept: "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(`Request failed with status ${response.status}.`, response.status);
  }

  const value: unknown = await response.json();
  const result = schema.safeParse(value);
  if (!result.success) {
    throw new ApiError("The API response did not match the expected contract.", 502);
  }
  return result.data;
}
```

<!-- artifact: src/features/products/model.ts; profiles: data,full -->
```ts
import { z } from "zod";

export const productSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
});

export const productPageSchema = z.object({
  items: z.array(productSchema),
  page: z.number().int().positive(),
  pageCount: z.number().int().nonnegative(),
});

export type ProductPage = z.infer<typeof productPageSchema>;

export function readPositivePage(value: string | string[] | undefined) {
  const candidate = Array.isArray(value) ? value[0] : value;
  const parsed = Number(candidate);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : 1;
}

export function readQuery(value: string | string[] | undefined) {
  const candidate = Array.isArray(value) ? value[0] : value;
  return candidate?.trim().slice(0, 80) ?? "";
}
```

<!-- artifact: src/features/products/query-provider.tsx; profiles: data,full -->
```tsx
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useState } from "react";

export function QueryProvider({ children }: { children: ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: false,
            staleTime: 30_000,
          },
        },
      }),
  );

  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
```

<!-- artifact: src/features/products/products-panel.tsx; profiles: data,full -->
```tsx
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { productPageSchema } from "@/features/products/model";
import { requestJson } from "@/lib/api-client";

export function ProductsPanel({
  initialPage = 1,
  initialQuery = "",
}: {
  initialPage?: number;
  initialQuery?: string;
}) {
  const queryClient = useQueryClient();
  const queryKey = ["products", { page: initialPage, query: initialQuery }] as const;
  const products = useQuery({
    queryKey,
    queryFn: () =>
      requestJson(
        `/api/products?page=${initialPage}&q=${encodeURIComponent(initialQuery)}`,
        productPageSchema,
      ),
  });
  const createProduct = useMutation({
    mutationFn: () =>
      requestJson("/api/products", productPageSchema, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "New reference" }),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });

  return (
    <section aria-labelledby="products-title" className="stack">
      <h2 id="products-title">Products</h2>
      <form action="/data" method="get" role="search" className="field">
        <label htmlFor="product-query">Search</label>
        <input id="product-query" name="q" defaultValue={initialQuery} />
        <button className="button" type="submit">
          Apply filter
        </button>
      </form>

      {products.isPending ? <p aria-live="polite">Loading products…</p> : null}
      {products.isError ? (
        <div role="alert">
          <p>Products could not be loaded.</p>
          <button className="button" type="button" onClick={() => void products.refetch()}>
            Retry
          </button>
        </div>
      ) : null}
      {products.data?.items.length === 0 ? <p>No products match this filter.</p> : null}
      {products.data?.items.length ? (
        <ul>
          {products.data.items.map((product) => (
            <li key={product.id}>{product.name}</li>
          ))}
        </ul>
      ) : null}

      {products.data ? (
        <nav aria-label="Product pages" className="links">
          {initialPage > 1 ? (
            <a href={`/data?page=${initialPage - 1}&q=${encodeURIComponent(initialQuery)}`}>
              Previous
            </a>
          ) : null}
          {initialPage < products.data.pageCount ? (
            <a href={`/data?page=${initialPage + 1}&q=${encodeURIComponent(initialQuery)}`}>Next</a>
          ) : null}
        </nav>
      ) : null}

      <button
        className="button"
        type="button"
        disabled={createProduct.isPending}
        onClick={() => createProduct.mutate()}
      >
        {createProduct.isPending ? "Adding…" : "Add example product"}
      </button>
      {createProduct.isError ? <p role="alert">The product could not be added.</p> : null}
      {createProduct.isSuccess ? <p role="status">Product added and list refreshed.</p> : null}
    </section>
  );
}
```

<!-- artifact: src/app/api/products/route.ts; profiles: data,full -->
```ts
import { NextResponse } from "next/server";

import { productPageSchema } from "@/features/products/model";

const products = [
  { id: "semantic-html", name: "Semantic HTML" },
  { id: "runtime-contracts", name: "Runtime contracts" },
  { id: "server-components", name: "Server Components" },
  { id: "focus-management", name: "Focus management" },
];

export async function GET(request: Request) {
  const url = new URL(request.url);
  const query = url.searchParams.get("q")?.trim().toLowerCase() ?? "";
  const page = Math.max(1, Number(url.searchParams.get("page")) || 1);

  if (query === "error") {
    return NextResponse.json({ message: "Deterministic failure" }, { status: 503 });
  }

  const filtered = products.filter((product) => product.name.toLowerCase().includes(query));
  const body = {
    items: filtered.slice((page - 1) * 2, page * 2),
    page,
    pageCount: Math.ceil(filtered.length / 2),
  };

  return NextResponse.json(productPageSchema.parse(body));
}

export async function POST() {
  return NextResponse.json(
    productPageSchema.parse({
      items: [{ id: "new-reference", name: "New reference" }],
      page: 1,
      pageCount: 1,
    }),
    { status: 201 },
  );
}
```

<!-- artifact: src/app/data/page.tsx; profiles: data,full -->
```tsx
import type { Metadata } from "next";

import { readPositivePage, readQuery } from "@/features/products/model";
import { ProductsPanel } from "@/features/products/products-panel";
import { QueryProvider } from "@/features/products/query-provider";

export const metadata: Metadata = { title: "Typed API data" };

export default async function DataPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string | string[]; q?: string | string[] }>;
}) {
  const params = await searchParams;

  return (
    <main id="main" className="shell">
      <h1>Typed API data</h1>
      <QueryProvider>
        <ProductsPanel
          initialPage={readPositivePage(params.page)}
          initialQuery={readQuery(params.q)}
        />
      </QueryProvider>
    </main>
  );
}
```
