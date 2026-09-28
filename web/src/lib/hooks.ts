import { useCallback, useEffect, useState, useSyncExternalStore } from "react";

export type Load<T> =
  | { state: "loading" }
  | { state: "error"; error: Error }
  | { state: "ready"; data: T; refreshing: boolean };

/** Fetch on mount and whenever `key` changes; optionally poll every `everyMs`. */
export function useApi<T>(fetcher: () => Promise<T>, key: string, everyMs?: number): Load<T> {
  const [load, setLoad] = useState<Load<T>>({ state: "loading" });
  const run = useCallback(fetcher, [key]);

  useEffect(() => {
    let alive = true;
    setLoad({ state: "loading" });
    const tick = (initial: boolean) => {
      if (!initial) setLoad((l) => (l.state === "ready" ? { ...l, refreshing: true } : l));
      run().then(
        (data) => alive && setLoad({ state: "ready", data, refreshing: false }),
        (error: Error) => alive && initial && setLoad({ state: "error", error }),
      );
    };
    tick(true);
    const id = everyMs ? window.setInterval(() => tick(false), everyMs) : undefined;
    return () => {
      alive = false;
      if (id) window.clearInterval(id);
    };
  }, [run, everyMs]);

  return load;
}

// --------------------------------------------------------------------- hash router

function subscribe(cb: () => void) {
  window.addEventListener("hashchange", cb);
  return () => window.removeEventListener("hashchange", cb);
}

/** The route is the hash path: `#/course/2026-09-28/R1C3` -> ["course", "2026-09-28", "R1C3"]. */
export function useRoute(): string[] {
  const hash = useSyncExternalStore(subscribe, () => window.location.hash);
  return hash
    .replace(/^#\/?/, "")
    .split("?")[0]!
    .split("/")
    .filter(Boolean)
    .map(decodeURIComponent);
}

export const href = (...parts: (string | number)[]) =>
  "#/" + parts.map((p) => encodeURIComponent(String(p))).join("/");
