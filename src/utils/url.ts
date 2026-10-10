/**
 * Read URL search params into a typed object, using `defaults` as both the
 * fallback for missing keys and the schema for type inference.
 *
 * Fields with a numeric default are parsed with Number(); all others are
 * treated as strings. All strings are lower-cased.
 */
export function readFromUrl<T extends Record<string, string | number | undefined>>(
  urlParams: URLSearchParams,
  defaults: T,
): T {
  const result = { ...defaults } as Record<string, string | number | undefined>
  for (const key of Object.keys(defaults)) {
    const raw = urlParams.get(key)
    if (raw === null) continue
    if (typeof defaults[key] === 'number') {
      const n = Number(raw)
      if (!isNaN(n)) result[key] = n
    } else {
      result[key] = raw.toLowerCase()
    }
  }
  return result as T
}

/**
 * Write `current` into `url`'s search params, omitting any field that equals
 * its default (or is undefined). All strings are lower-cased.
 */
export function syncToUrl<T extends Record<string, string | number | undefined>>(
  current: T,
  defaults: T,
  url: URL,
): void {
  for (const key of Object.keys(defaults)) {
    const val = (current as Record<string, unknown>)[key]
    if (val === undefined || val === defaults[key])
      url.searchParams.delete(key)
    else
      url.searchParams.set(key, String(val).toLowerCase())
  }
}
