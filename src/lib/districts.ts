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
