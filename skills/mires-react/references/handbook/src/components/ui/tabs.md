# Compound tabs primitive

The compound API avoids boolean-prop proliferation and keeps markup flexible.
The provider exposes only the state and actions that descendants need.

<!-- artifact: src/components/ui/tabs.tsx; profiles: base,forms,data,auth,realtime,full -->
```tsx
"use client";

import {
  createContext,
  type KeyboardEvent,
  type ReactNode,
  useContext,
  useId,
  useRef,
  useState,
} from "react";

type TabsContextValue = {
  activeValue: string;
  id: string;
  select: (value: string) => void;
};

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabs() {
  const value = useContext(TabsContext);
  if (!value) {
    throw new Error("Tabs components must be rendered inside Tabs.Root");
  }
  return value;
}

function Root({
  "aria-label": ariaLabel,
  children,
  defaultValue,
}: {
  "aria-label": string;
  children: ReactNode;
  defaultValue: string;
}) {
  const [activeValue, setActiveValue] = useState(defaultValue);
  const id = useId();

  return (
    <TabsContext value={{ activeValue, id, select: setActiveValue }}>
      <section className="tabs" aria-label={ariaLabel}>
        {children}
      </section>
    </TabsContext>
  );
}

function List({ children }: { children: ReactNode }) {
  const listRef = useRef<HTMLDivElement>(null);

  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) {
      return;
    }

    const tabs = Array.from(
      listRef.current?.querySelectorAll<HTMLButtonElement>('[role="tab"]') ?? [],
    );
    const current = tabs.indexOf(document.activeElement as HTMLButtonElement);
    if (current < 0) {
      return;
    }

    event.preventDefault();
    const target =
      event.key === "Home"
        ? 0
        : event.key === "End"
          ? tabs.length - 1
          : (current + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
    tabs[target]?.focus();
    tabs[target]?.click();
  }

  return (
    <div ref={listRef} className="tab-list" role="tablist" onKeyDown={onKeyDown}>
      {children}
    </div>
  );
}

function Tab({ children, value }: { children: ReactNode; value: string }) {
  const tabs = useTabs();
  const selected = tabs.activeValue === value;

  return (
    <button
      id={`${tabs.id}-tab-${value}`}
      className="tab"
      type="button"
      role="tab"
      aria-controls={`${tabs.id}-panel-${value}`}
      aria-selected={selected}
      tabIndex={selected ? 0 : -1}
      onClick={() => tabs.select(value)}
    >
      {children}
    </button>
  );
}

function Panel({ children, value }: { children: ReactNode; value: string }) {
  const tabs = useTabs();
  if (tabs.activeValue !== value) {
    return null;
  }

  return (
    <div
      id={`${tabs.id}-panel-${value}`}
      className="tab-panel"
      role="tabpanel"
      aria-labelledby={`${tabs.id}-tab-${value}`}
      tabIndex={0}
    >
      {children}
    </div>
  );
}

export const Tabs = {
  Root,
  List,
  Tab,
  Panel,
};
```
