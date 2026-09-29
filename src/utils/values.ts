import p1Raw from '../../.data/presidential_values/p1.json'
import p2Raw from '../../.data/presidential_values/p2.json'
import p5Raw from '../../.data/presidential_values/p5.json'
import dimensionsRaw from '../../.data/dimensions/presidential_elections.json'
import statesRaw from "../data/states.json";

export type Scenario = 'p1' | 'p2' | 'p5'
export type ValueType = 'av' | 'pv' | 'wvv'
export type PopVar = 'ap' | 'vap' | 'vep' | 'vp'
export type Party = 'democrat' | 'republican' | 'other'

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
const p5Data = p5Raw as Record<string, YearStateData>

// Build dimensions winner lookups: year -> (state_po ->) Party | null
const dimensionsNationalWinner: Record<string, Party | null> = {}
const dimensionsStateWinner: Record<string, Record<string, Party | null>> = {}
const statesByPo = new Map(statesRaw.map(({ id, name }) => [id.toUpperCase(), name]))

for (const yearData of dimensionsRaw as Array<{
  year: number
  winning_party: string | null
  states: Array<{ state: string, state_po: string; winning_party: string | null }>
}>) {
  const yearKey = String(yearData.year)
  dimensionsNationalWinner[yearKey] = (yearData.winning_party as Party | null) || null
  dimensionsStateWinner[yearKey] = {}
  for (const s of yearData.states) {
    dimensionsStateWinner[yearKey][s.state_po] = (s.winning_party as Party | null) || null
  }
}

const allStatePOs = [...statesByPo.keys()].sort()

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
  _winner: Party | null,
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
      state: state,
      value: null,
      winningParty: null,
      isFocus: state_po === focusState,
    }))
  }

  if (scenario === 'p1') {
    const national = p1Data[yearKey]
    const nationalWinner = dimensionsNationalWinner[yearKey] ?? null
    const nationalValue = national
      ? extractValue(national, value, popVar, nationalWinner)
      : null

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
      value: record ? extractValue(record, value, popVar, winner) : null,
      winningParty: winner,
      isFocus: state_po === focusState,
    }
  })
}
