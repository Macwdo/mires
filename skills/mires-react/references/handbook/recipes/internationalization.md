# Internationalization

Resolve locale on the server from a validated route segment, account, or
request preference. Keep messages structured and typed, format dates and
numbers with `Intl`, set the document language and direction, and do not build
sentences by concatenating translated fragments.

<!-- artifact: src/lib/i18n.ts; profiles: full -->
```ts
const messages = {
  en: {
    heading: "Frontend standards",
    itemCount: (count: number) => new Intl.NumberFormat("en").format(count),
  },
  pt: {
    heading: "Padrões de frontend",
    itemCount: (count: number) => new Intl.NumberFormat("pt-BR").format(count),
  },
} as const;

export type Locale = keyof typeof messages;

export function isLocale(value: string): value is Locale {
  return Object.hasOwn(messages, value);
}

export function getMessages(locale: Locale) {
  return messages[locale];
}
```
