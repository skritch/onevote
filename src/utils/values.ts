import p1Raw from '../../.data/presidential_values/p1.json'
import p2Raw from '../../.data/presidential_values/p2.json'
import p5Raw from '../../.data/presidential_values/p5.json'

export type Scenario = 'p1' | 'p2' | 'p5'
export type ValueType = 'av' | 'pv' | 'wvv'
export type PopVar = 'ap' | 'vap' | 'vep' | 'vp'
export type Party = 'democrat' | 'republican' | 'other'

export interface PlotRow {
  state: string       // uppercase state_po, e.g. 'AL'
  value: number | null
  winningParty: Party | null
  isFocus: boolean
}

type StateValues = Record<string, number | null>
type YearStateData = Record<string, StateValues>

const p1Data = p1Raw as Record<string, StateValues>
const p2Data = p2Raw as Record<string, YearStateData>
const p5Data = p5Raw as Record<string, YearStateData>

export const partyColors: Record<string, string> = {
  democrat: '#4169e1',
  republican: '#a0372e',
  other: '#6c757d',
  unknown: '#adb5bd',
}

// p2 is cleanest: losing party wvv is always 0
function inferWinner(record: StateValues): Party | null {
  const d = Number(record['wvv_democrat'] ?? 0)
  const r = Number(record['wvv_republican'] ?? 0)
  if (d > r) return 'democrat'
  if (r > d) return 'republican'
  if (Number(record['wvv_other'] ?? 0) > 0) return 'other'
  return null
}

function extractValue(
  record: StateValues,
  value: ValueType,
  popVar: PopVar | undefined,
  winner: Party | null,
): number | null {
  if (value === 'wvv') {
    if (!winner) return null
    const v = record[`wvv_${winner}`]
    return v == null ? null : (v as number)
  }
  const pop = popVar ?? (value === 'av' ? 'ap' : 'vap')
  const v = record[`${value}_${pop}`]
  return v == null ? null : (v as number)
}

/**
 * Returns one row per state for the given scenario/year/value combination.
 * Returns [] if the year is not in the data.
 * Individual rows have value=null when that combination is unavailable (e.g. vep before 1980).
 * Always uses p2 data to determine state-level winning party (for consistent bar coloring).
 */
export function getPlotRows(
  scenario: Scenario,
  year: number,
  focusState: string,   // uppercase state_po, e.g. 'NY'
  value: ValueType,
  popVar?: PopVar,
): PlotRow[] {
  const yearKey = String(year)
  const p2Year = p2Data[yearKey]
  if (!p2Year) return []

  if (scenario === 'p1') {
    const national = p1Data[yearKey]
    if (!national) return []
    const nationalWinner = inferWinner(national)
    const nationalValue = value === 'wvv'
      ? (nationalWinner ? (national[`wvv_${nationalWinner}`] as number) : null)
      : extractValue(national, value, popVar, null)

    return Object.keys(p2Year).map(state => ({
      state,
      value: nationalValue,
      winningParty: inferWinner(p2Year[state]),  // state-level color
      isFocus: state === focusState,
    }))
  }

  const scenarioYear = (scenario === 'p5' ? p5Data : p2Data)[yearKey]
  if (!scenarioYear) return []

  return Object.entries(scenarioYear).map(([state, record]) => {
    const winner = inferWinner(p2Year[state])  // always from p2
    return {
      state,
      value: extractValue(record, value, popVar, winner),
      winningParty: winner,
      isFocus: state === focusState,
    }
  })
}
