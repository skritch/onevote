import p1Raw from '../../.data/presidential_values/p1.json'
import p2Raw from '../../.data/presidential_values/p2.json'
import p3Raw from '../../.data/presidential_values/p3.json'
import p5Raw from '../../.data/presidential_values/p5.json'
import statesRaw from "../data/states.json"
import { dimensionsNationalWinner, dimensionsStateWinner } from './elections.js'
import type { Party } from './elections.js'

export type { Party } from './elections.js'
export type { StateDimension } from './elections.js'
export { candidatesByYear } from './elections.js'
export { getStateDimension } from './elections.js'

export type Scenario = 'p1' | 'p2' | 'p5'
export type ValueType = 'av' | 'pv' | 'wvv'
export type PopVar = 'ap' | 'vap' | 'vep' | 'vp'

export interface PlotRow {
  state_po: string // uppercase state_po, e.g. 'AL'
  state: string
  value: number | null
  winningParty: Party | null
  isFocus: boolean
}

type StateValues = Record<string, number | null>
type YearStateData = Record<string, StateValues>

const p1Data = p1Raw as Record<string, StateValues>
const p2Data = p2Raw as Record<string, YearStateData>
// p3: year → state_po → district_number → values (ME/NE split electors by district)
const p3Data = p3Raw as Record<string, Record<string, Record<string, StateValues>>>
const p5Data = p5Raw as Record<string, YearStateData>

export const statesByPo = new Map(statesRaw.map(({ id, name }) => [id.toUpperCase(), name]))

export const partyColors: Record<string, string> = {
  democrat: '#4169e1',
  republican: '#a0372e',
  other: '#6c757d',
  unknown: '#adb5bd',
}

function extractValue(
  record: StateValues,
  value: ValueType,
  popVar: PopVar | undefined,
): number | null {
  const pop = popVar ?? (value === 'av' ? 'ap' : 'vap')
  const v = record[`${value}_${pop}`]
  return v == null ? null : (v as number)
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
  focusState: string,   // uppercase state_po, e.g. 'NY'
  value: ValueType,
  popVar?: PopVar,
): PlotRow[] {
  const yearKey = String(year)
  const stateWinners = dimensionsStateWinner[yearKey]

  if (!stateWinners) {
    return Array.from(statesByPo.entries()).map(([state_po, state]) => ({
      state_po,
      state,
      value: null,
      winningParty: null,
      isFocus: state_po === focusState,
    }))
  }

  if (scenario === 'p1') {
    const national = p1Data[yearKey]
    const nationalWinner = dimensionsNationalWinner[yearKey] ?? null
    const nationalValue = national ? extractValue(national, value, popVar) : null

    return Array.from(statesByPo.entries()).map(([state_po, state]) => ({
      state_po,
      state,
      value: nationalValue,
      winningParty: stateWinners[state_po] ?? null,
      isFocus: state_po === focusState,
    }))
  }

  const scenarioYear = (scenario === 'p5' ? p5Data : p2Data)[yearKey]
  if (!scenarioYear) {
    return Array.from(statesByPo.entries()).map(([state_po, state]) => ({
      state_po,
      state,
      value: null,
      winningParty: stateWinners[state_po] ?? null,
      isFocus: state_po === focusState,
    }))
  }

  return Array.from(statesByPo.entries()).map(([state_po, state]) => {
    const winner = stateWinners[state_po] ?? null
    const record = scenarioYear[state_po]
    return {
      state_po,
      state,
      value: record ? extractValue(record, value, popVar) : null,
      winningParty: winner,
      isFocus: state_po === focusState,
    }
  })
}

/**
 * Returns the value for a single state. For p3 (actual EC), district "1" is used
 * as the state-level representative value (all districts identical except ME/NE).
 */
export function getStateValue(
  scenario: string,
  year: number,
  state_po: string,
  value: ValueType,
  popVar?: PopVar,
): number | null {
  const yearKey = String(year)
  const po = state_po.toUpperCase()
  const pop = popVar ?? (value === 'av' ? 'ap' : 'vap')
  const key = `${value}_${pop}`

  if (scenario === 'p1') {
    const national = p1Data[yearKey]
    return national ? ((national[key] as number | null) ?? null) : null
  }

  if (scenario === 'p3') {
    const yearData = p3Data[yearKey]
    if (!yearData) return null
    const stateDistricts = yearData[po]
    if (!stateDistricts) return null
    const first = stateDistricts['1'] ?? Object.values(stateDistricts)[0]
    return first ? ((first[key] as number | null) ?? null) : null
  }

  const data = scenario === 'p5' ? p5Data : p2Data
  const yearData = data[yearKey]
  if (!yearData) return null
  const record = yearData[po]
  return record ? ((record[key] as number | null) ?? null) : null
}
