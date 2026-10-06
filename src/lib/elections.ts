import dimensionsRaw from '../../.data/dimensions/presidential_elections.json'
import electionsRaw from '../data/elections.json'
import { initCap } from '../utils/strings.js'
import type { Party } from './party.js'
import type { StatePO } from './states.js'

export type Office = "president" | "house" | "senate"
export const OFFICES = ["president", "house", "senate"] as const

export const officesByName: Record<string, Office> = {
  Presidential: "president",
  House: "house",
  Senate: "senate",
}

export type StateDimension = {
  year: number
  state: string
  statePO: StatePO
  apportionmentPopulation: number | null
  vapEstimate: number | null
  vepEstimate: number | null
  votesTotal: number | null
  votesDemocrat: number | null
  votesRepublican: number | null
  votesOther: number | null
  winningParty: Party | null
  electors: number | null
  electorsDemocrat: number | null
  electorsRepublican: number | null
  electorsOther: number | null
}

export type DistrictDimension = {
  districtCode: string
  apportionmentPopulation: number | null
  votesTotal: number | null
  votesDemocrat: number | null
  votesRepublican: number | null
  votesOther: number | null
  winningParty: Party | null
  electors: number | null
  electorsDemocrat: number | null
  electorsRepublican: number | null
  electorsOther: number | null
}

type RawStateDimension = {
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
  districts?: RawDistrictDimension[]
}

type RawDistrictDimension = {
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

function toStateDimension(raw: RawStateDimension): StateDimension {
  return {
    year: raw.year,
    state: raw.state,
    statePO: raw.state_po,
    apportionmentPopulation: raw.apportionment_population,
    vapEstimate: raw.vap_estimate,
    vepEstimate: raw.vep_estimate,
    votesTotal: raw.votes_total,
    votesDemocrat: raw.votes_democrat,
    votesRepublican: raw.votes_republican,
    votesOther: raw.votes_other,
    winningParty: raw.winning_party ? initCap(raw.winning_party) as Party : null,
    electors: raw.electors,
    electorsDemocrat: raw.electors_democrat,
    electorsRepublican: raw.electors_republican,
    electorsOther: raw.electors_other,
  }
}

function toDistrictDimension(raw: RawDistrictDimension): DistrictDimension {
  return {
    districtCode: raw.district_code,
    apportionmentPopulation: raw.apportionment_population,
    votesTotal: raw.votes_total,
    votesDemocrat: raw.votes_democrat,
    votesRepublican: raw.votes_republican,
    votesOther: raw.votes_other,
    winningParty: raw.winning_party ? initCap(raw.winning_party) as Party : null,
    electors: raw.electors,
    electorsDemocrat: raw.electors_democrat,
    electorsRepublican: raw.electors_republican,
    electorsOther: raw.electors_other,
  }
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

const allDimYears = (dimensionsRaw as Array<{ year: number }>).map(d => d.year)

function resolveYear(year: number): number {
  if (allDimYears.includes(year)) return year
  const past = allDimYears.filter(y => y < year)
  return past.length > 0 ? Math.max(...past) : Math.min(...allDimYears)
}

export function getStateDimension(year: number, statePO: StatePO): StateDimension | null {
  const resolved = resolveYear(year)
  const yearData = (dimensionsRaw as Array<{ year: number; states: RawStateDimension[] }>)
    .find(d => d.year === resolved)
  if (!yearData) return null
  const raw = yearData.states.find(s => s.state_po === statePO)
  return raw ? toStateDimension(raw) : null
}

export function getDistrictDimension(year: number, statePO: StatePO, districtId: string): DistrictDimension | null {
  const resolved = resolveYear(year)
  const yearData = (dimensionsRaw as Array<{ year: number; states: RawStateDimension[] }>)
    .find(d => d.year === resolved)
  if (!yearData) return null
  const stateEntry = yearData.states.find(s => s.state_po === statePO)
  if (!stateEntry?.districts) return null
  // district_codes in data use leading zeros ("01"), districtId may not ("1")
  const raw = stateEntry.districts.find(d =>
    d.district_code === districtId || d.district_code === districtId.padStart(2, '0')
  )
  return raw ? toDistrictDimension(raw) : null
}
