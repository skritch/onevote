export type DistrictIndex = {
  yearToCongress: Record<string, number>;
  districtIdsByCongress: Record<string, string[]>;
}

export function getDistrictIdsForYear(index: DistrictIndex, year: number): string[] {
  const congress = index.yearToCongress[String(year)] ?? Math.max(...Object.values(index.yearToCongress));
  return index.districtIdsByCongress[String(congress)] ?? [];
}

export function getCongressForYear(index: DistrictIndex, year: number): number {
  return index.yearToCongress[String(year)] ?? Math.max(...Object.values(index.yearToCongress));
}
