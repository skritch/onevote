import dimensionsRaw from '../../.data/dimensions/presidential_elections.json'
import electionsRaw from '../data/elections.json'

export type Office = "president" | "house" | "senate"
export type Party = 'democrat' | 'republican' | 'other'

export const officesByName: Record<string, Office> = {
  Presidential: "president",
  House: "house",
  Senate: "senate",
}

export type StateDimension = {
  year: number
  state: string
  state_po: string
  apportionment_population: number | null
  vap_estimate: number | null
  vep_estimate: number | null
  votes_total: number | null
  votes_democrat: number | null
  votes_republican: number | null
  votes_other: number | null
  winning_party: string | null
  electors: number | null
  electors_democrat: number | null
  electors_republican: number | null
  electors_other: number | null
}

export type DistrictDimension = {
  district_code: string
  apportionment_population: number | null
  votes_total: number | null
  votes_democrat: number | null
  votes_republican: number | null
  votes_other: number | null
  winning_party: string | null
  electors: number | null
  electors_democrat: number | null
  electors_republican: number | null
  electors_other: number | null
}

type RawYearEntry = {
  year: number
  winning_party: string | null
  states: Array<{ state_po: string; winning_party: string | null }>
}

// Winner lookups built once at module load: year → Party | null
export const dimensionsNationalWinner: Record<string, Party | null> = {}
export const dimensionsStateWinner: Record<string, Record<string, Party | null>> = {}

for (const yearData of dimensionsRaw as RawYearEntry[]) {
  const yearKey = String(yearData.year)
  dimensionsNationalWinner[yearKey] = (yearData.winning_party as Party | null) || null
  dimensionsStateWinner[yearKey] = {}
  for (const s of yearData.states) {
    dimensionsStateWinner[yearKey][s.state_po] = (s.winning_party as Party | null) || null
  }
}

export const candidatesByYear: Record<number, { democrat: string; republican: string }> =
  Object.fromEntries(
    electionsRaw
      .filter((e): e is typeof e & { candidate_democrat: string; candidate_republican: string } =>
        'candidate_democrat' in e && 'candidate_republican' in e
      )
      .map(e => [e.year, { democrat: e.candidate_democrat, republican: e.candidate_republican }])
  )

type RawStateEntry = StateDimension & { districts?: DistrictDimension[] }

const allDimYears = (dimensionsRaw as Array<{ year: number }>).map(d => d.year)

function resolveYear(year: number): number {
  if (allDimYears.includes(year)) return year
  const past = allDimYears.filter(y => y < year)
  return past.length > 0 ? Math.max(...past) : Math.min(...allDimYears)
}

export function getStateDimension(year: number, state_po: string): StateDimension | null {
  const resolved = resolveYear(year)
  const yearData = (dimensionsRaw as Array<{ year: number; states: RawStateEntry[] }>)
    .find(d => d.year === resolved)
  if (!yearData) return null
  return yearData.states.find(s => s.state_po === state_po) ?? null
}

export function getDistrictDimension(year: number, state_po: string, districtId: string): DistrictDimension | null {
  const resolved = resolveYear(year)
  const yearData = (dimensionsRaw as Array<{ year: number; states: RawStateEntry[] }>)
    .find(d => d.year === resolved)
  if (!yearData) return null
  const stateEntry = yearData.states.find(s => s.state_po === state_po)
  if (!stateEntry?.districts) return null
  // district_codes in data use leading zeros ("01"), districtId may not ("1")
  return stateEntry.districts.find(d =>
    d.district_code === districtId || d.district_code === districtId.padStart(2, '0')
  ) ?? null
}
