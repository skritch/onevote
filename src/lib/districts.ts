import districtResultsRaw from '../data/district_results.json'

export type DistrictIndex = {
  yearToCongress: Record<string, number>;
}

export function getCongressForYear(index: DistrictIndex, year: number): number {
  return index.yearToCongress[String(year)] ?? Math.max(...Object.values(index.yearToCongress));
}

export type DistrictResult = {
  winningParty: string | null;
}

export type DistrictResults = Record<string, Record<string, Record<string, DistrictResult>>>

export const districtResults = districtResultsRaw as DistrictResults

export function getDistrictIdsForYear(statePO: string, year: number): string[] {
  return Object.keys(districtResults[String(year)]?.[statePO] ?? {});
}
