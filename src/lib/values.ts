import p1Raw from '../data/values/p1.json'
import p2Raw from '../data/values/p2.json'
import p3Raw from '../data/values/p3.json'
import p3StateRaw from '../data/values/p3_state.json'
import p4Raw from '../data/values/p4.json'
import p4StateRaw from '../data/values/p4_state.json'
import p5Raw from '../data/values/p5.json'
import { states } from './states.js'
import type { StatePO } from './states.js'
import { dimensionsNationalWinner, dimensionsStateWinner } from './elections.js'
import type { Party } from './party.js'
export type { StateDimension, DistrictDimension } from './elections.js'
export { candidatesByYear } from './elections.js'
export { getStateDimension, getDistrictDimension } from './elections.js'

export type Scenario = 'p1' | 'p2' | 'p3' | 'p4' | 'p5'
export type ValueType = 'av' | 'pv' | 'wvv'
export type PopVar = 'ap' | 'vap' | 'vep' | 'vp'

export interface PlotRow {
  statePO: StatePO
  state: string
  value: number | null
  party: string | null   // which party this bar represents (for WVV); null = state-level
  winningParty: Party | null
  isFocus: boolean
}

const partyToWvvSuffix: Record<string, string> = { democrat: 'd', republican: 'r', other: 'o' }

type ValueEntries = Record<string, number | null>

const p1Data = p1Raw as Record<string, ValueEntries>
const p2Data = p2Raw as Record<string, Record<string, ValueEntries>>
// p3/p4: year → statePO → district_number → values
const p3Data = p3Raw as Record<string, Record<string, Record<string, ValueEntries>>>
const p3StateData = p3StateRaw as Record<string, Record<string, ValueEntries>>
const p4Data = p4Raw as Record<string, Record<string, Record<string, ValueEntries>>>
const p4StateData = p4StateRaw as Record<string, Record<string, ValueEntries>>
const p5Data = p5Raw as Record<string, Record<string, ValueEntries>>

export const statesByPo = new Map(states.map(({ statePO, stateName }) => [statePO, stateName]))


function extractValue(
  record: ValueEntries,
  value: ValueType,
  popVar: PopVar | undefined,
  party?: string,
): number | null {
  if (value === 'wvv') {
    const suffix = partyToWvvSuffix[(party ?? 'democrat').toLowerCase()] ?? 'd'
    const v = record[`wvv_vp_${suffix}`]
    return v ?? null
  }
  const pop = popVar ?? (value === 'av' ? 'ap' : 'vap')
  const v = record[`${value}_${pop}`]
  return v ?? null
}

/**
 * Returns the available district numbers for a state under a given scenario/year.
 * Returns [] for scenarios that don't use districts (p1/p2/p5) or years with no data.
 * For p3, only ME and NE have multiple districts; all other states return ['1'].
 * For p4, every state has one entry per congressional district.
 */
export function getDistrictsForState(
  scenario: string,
  year: number,
  statePO: StatePO,
): string[] {
  if (scenario !== 'p3' && scenario !== 'p4') return []
  const data = scenario === 'p3' ? p3Data : p4Data
  const yearData = data[String(year)]
  if (!yearData) return []
  const stateData = yearData[statePO]
  if (!stateData) return []
  return Object.keys(stateData).filter(d => Object.keys(stateData[d]).length > 0)
}

/**
 * Returns one row per state for the given scenario/year/value combination.
 * Returns empty (value=null) rows for all states in alphabetical order when the year is not in the data.
 * Individual rows have value=null when that combination is unavailable (e.g. vep before 1980).
 * Uses dimensions data to determine state-level winning party (for consistent bar coloring).
 */
export function getPlotRows(
  scenario: Scenario,
  year: number,
  focusStatePO: StatePO | StatePO[],
  value: ValueType,
  popVar?: PopVar,
  party?: string,
): PlotRow[] {
  const yearKey = String(year)
  const stateWinners = dimensionsStateWinner[yearKey]
  const focusSet = Array.isArray(focusStatePO) ? new Set(focusStatePO) : new Set([focusStatePO])
  const isFocus = (po: StatePO) => focusSet.has(po)

  if (!stateWinners) {
    return Array.from(statesByPo.entries()).map(([statePO, state]) => ({
      statePO,
      state,
      value: null,
      party: party ?? null,
      winningParty: null,
      isFocus: isFocus(statePO),
    }))
  }

  if (scenario === 'p1') {
    const national = p1Data[yearKey]
    const nationalValue = national ? extractValue(national, value, popVar, party) : null

    return Array.from(statesByPo.entries()).map(([statePO, state]) => ({
      statePO,
      state,
      value: nationalValue,
      party: party ?? null,
      winningParty: stateWinners[statePO] ?? null,
      isFocus: isFocus(statePO),
    }))
  }

  const stateDataMap: Record<string, Record<string, Record<string, ValueEntries>>> = { p3: p3StateData, p4: p4StateData, p5: p5Data }
  const scenarioYear = (stateDataMap[scenario] ?? p2Data)[yearKey]
  if (!scenarioYear) {
    return Array.from(statesByPo.entries()).map(([statePO, state]) => ({
      statePO,
      state,
      value: null,
      party: party ?? null,
      winningParty: stateWinners[statePO] ?? null,
      isFocus: isFocus(statePO),
    }))
  }

  return Array.from(statesByPo.entries()).map(([statePO, state]) => {
    const winner = stateWinners[statePO] ?? null
    const record = scenarioYear[statePO]
    return {
      statePO,
      state,
      value: record ? extractValue(record, value, popVar, party) : null,
      party: party ?? null,
      winningParty: winner,
      isFocus: isFocus(statePO),
    }
  })
}

/**
 * Returns the value for a single state or district.
 * For p3/p4, pass `district` (e.g. '1', '2') to get a district-specific value;
 * omit or pass undefined to get the default (district '1', or first available).
 */
export function getStateValue(
  scenario: string,
  year: number,
  statePO: StatePO,
  value: ValueType,
  popVar?: PopVar,
  district?: string,
  party?: string,
): number | null {
  const yearKey = String(year)

  if (scenario === 'p1') {
    const national = p1Data[yearKey]
    return national ? extractValue(national, value, popVar, party) : null
  }

  if (scenario === 'p3' || scenario === 'p4') {
    if (district) {
      const data = scenario === 'p3' ? p3Data : p4Data
      const yearData = data[yearKey]
      if (!yearData) return null
      const stateDistricts = yearData[statePO]
      if (!stateDistricts) return null
      const record = stateDistricts[district]
      return record ? extractValue(record, value, popVar, party) : null
    }
    const stateData = scenario === 'p3' ? p3StateData : p4StateData
    const record = stateData[yearKey]?.[statePO]
    return record ? extractValue(record, value, popVar, party) : null
  }

  const data = scenario === 'p5' ? p5Data : p2Data
  const yearData = data[yearKey]
  if (!yearData) return null
  const record = yearData[statePO]
  return record ? extractValue(record, value, popVar, party) : null
}
