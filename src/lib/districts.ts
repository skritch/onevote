// Lightweight version of DistrictData with SVG paths stripped — safe to send to the client for all states.
export type DistrictIndex = {
  yearToCongress: Record<string, number>;
  districtIdsByCongress: Record<string, string[]>;
}

export function buildDistrictIndex(data: DistrictData): DistrictIndex {
  return {
    yearToCongress: data.yearToCongress,
    districtIdsByCongress: Object.fromEntries(
      Object.entries(data.districtsByCongress).map(([congress, districts]) => [
        congress,
        Object.keys(districts).sort((a, b) => {
          const na = Number(a), nb = Number(b);
          if (!isNaN(na) && !isNaN(nb)) return na - nb;
          if (!isNaN(na)) return -1;
          if (!isNaN(nb)) return 1;
          return a.localeCompare(b);
        }),
      ]),
    ),
  };
}

export function getDistrictIdsForYear(index: DistrictIndex, year: number): string[] {
  const congress = index.yearToCongress[String(year)] ?? Math.max(...Object.values(index.yearToCongress));
  return index.districtIdsByCongress[String(congress)] ?? [];
}

export type DistrictData = {
  yearToCongress: Record<string, number>
  districtsByCongress: Record<string, Record<string, string>>
  viewboxByCongress?: Record<string, string>
}

export function getCongressForYear(districtData: DistrictData, year: number): number {
  return (
    districtData.yearToCongress[String(year)] ??
    Math.max(...Object.values(districtData.yearToCongress))
  )
}

export function getAvailableDistrictIds(districtData: DistrictData, year: number): string[] {
  const congress = getCongressForYear(districtData, year)
  if (congress == null) return []
  return Object.keys(districtData.districtsByCongress[String(congress)] ?? {}).sort(
    (a, b) => {
      const na = Number(a), nb = Number(b)
      if (!isNaN(na) && !isNaN(nb)) return na - nb
      if (!isNaN(na)) return -1
      if (!isNaN(nb)) return 1
      return a.localeCompare(b)
    },
  )
}
