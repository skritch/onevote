import { districtIndex } from "./districts";
import { type Year } from "./manifest";
import type { StatePO } from "./states";

  
export type PathEntry = { id: string; d: string };
export type SvgData = { viewBox: string; paths: PathEntry[] };


export function urlForStateYear(po: StatePO, year: Year): string | null {
  if (!districtIndex[po]) { return null }
  const cong = districtIndex[po]
    .yearToCongress[String(year)] 
    ?? Math.max(...Object.values(districtIndex[po].yearToCongress));
  return `${import.meta.env.BASE_URL}maps/${po}-${cong}.svg`;
}

export function urlsByYear(po: StatePO) {
  const result: Record<Year, string> = {}
  if (!districtIndex[po]) { return result }
  Object.entries(districtIndex[po].yearToCongress)
    .forEach(([year, cong]) => {
      result[Number(year)] = `${import.meta.env.BASE_URL}maps/${po}-${cong}.svg`;
    })
  return result
} 
  
export async function fetchSvgData(url: string): Promise<SvgData | null> {
  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    const text = await res.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(text, "image/svg+xml");
    const svg = doc.querySelector("svg");
    if (!svg) return null;
    const viewBox = svg.getAttribute("viewBox") ?? "14 14 772 572";
    const paths = Array.from(svg.querySelectorAll("path"))
      .map((p) => ({ id: p.getAttribute("id") ?? "", d: p.getAttribute("d") ?? "" }))
      .filter((p) => p.id && p.d);
    return { viewBox, paths };
  } catch {
    return null;
  }
}