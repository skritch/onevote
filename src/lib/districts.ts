import districtResultsRaw from '../data/district_results.json'
import districtIndexRaw from "../data/district_index.json";
import type { Year } from './manifest';
import type { StatePO } from './states';


export type DistrictIndexEntry = {
  yearToCongress: Record<string, number>;
}

export const districtIndex = districtIndexRaw as Record<string, DistrictIndexEntry>;


export type DistrictResult = {
  winningParty: string | null;
}

export type DistrictResults = Record<string, Record<string, Record<string, DistrictResult>>>

export const districtResults = districtResultsRaw as DistrictResults

export function getDistrictIdsForYear(statePO: string, year: number): string[] {
  return Object.keys(districtResults[String(year)]?.[statePO] ?? {});
}

export function getDistrictResultsByYear(statePO: StatePO): Record<Year, Record<string, DistrictResult>> {
  const resultsByYear: Record<Year, Record<string, DistrictResult>> = {}
  Object.entries(districtResults)
      .forEach(([year, results]) => { resultsByYear[Number(year)] = results[statePO]})
  return resultsByYear
}
