import type { Scenario, ValueType, PopVar } from './values.js'

export type YearConstraint = {
  years?: number[]
  before?: number    // applies if year < before
  from?: number      // applies if year >= from
  excludePopVars?: PopVar[]
  excludeValues?: ValueType[]
  excludeScenarios?: string[]
}

export const valueNames: Record<ValueType, string> = {
  av: 'Apportionment Value',
  pv: 'Pivotality Value',
  wvv: 'Wasted Vote Value',
}

export const valueShortNames: Record<ValueType, string> = {
  av: 'AV',
  pv: 'PV',
  wvv: 'WVV',
}

export const popVarNames: Record<PopVar, string> = {
  ap: 'Apportionment Population',
  vap: 'Voting Age Population',
  vep: 'Voting-Eligible Population',
  vp: 'Votes Cast',
}

export const popVarShortNames: Record<PopVar, string> = {
  ap: 'AP',
  vap: 'VAP',
  vep: 'VEP',
  vp: 'VP',
}

export const scenarioNames: Record<Scenario, string> = {
  p1: 'National General Election',
  p2: 'Simplified Electoral College',
  p5: 'Proportional Electors',
}

export const scenarioShortNames: Record<Scenario, string> = {
  p1: 'General',
  p2: 'Simplified EC',
  p5: 'Proportional EC',
}

// Pop vars applicable per value type.
export const validPopVars: Partial<Record<ValueType, PopVar[]>> = {
  av: ['ap', 'vap', 'vep', 'vp'],
  pv: ['vap', 'vep', 'vp'],
  wvv: ['vp'],
}

// Default selections (used for URL param omission — only non-defaults are added to URL)
export const defaultValue: ValueType = 'av'
export const defaultPopVar: Partial<Record<ValueType, PopVar>> = {
  av: 'ap',
  pv: 'vap',
}

// Value types available per scenario
export const validValues: Record<Scenario, ValueType[]> = {
  p1: ['av', 'pv', 'wvv'],
  p2: ['av', 'pv', 'wvv'],
  p5: ['av', 'wvv'],
}

// Per-year restrictions applied on top of scenario-based ones.
// av+ap is always the fallback — constraints here must never exclude both.
export const yearConstraints: YearConstraint[] = [
  // 2028 has no vote results and only AP, so PV and WVV are unavailable
  { years: [2028], excludePopVars: ['vap', 'vep', 'vp'], excludeValues: ['pv', 'wvv'] },
  // 1976 is missing VAP/VEP data
  { years: [1976], excludePopVars: ['vap', 'vep'] },
  // District data only available from 2012 onward
  { before: 2012, excludeScenarios: ['p3', 'p4'] },
]

export function getValidForYear(
  year: number,
  scenario: Scenario,
): { values: ValueType[]; popVarsFor: (v: ValueType) => PopVar[] } {
  const excludedPop = new Set<PopVar>()
  const excludedVal = new Set<ValueType>()

  for (const c of yearConstraints) {
    const matches =
      (c.years != null && c.years.includes(year)) ||
      (c.before != null && year < c.before) ||
      (c.from != null && year >= c.from)
    if (matches) {
      c.excludePopVars?.forEach(p => excludedPop.add(p))
      c.excludeValues?.forEach(v => excludedVal.add(v))
    }
  }

  const popVarsFor = (v: ValueType): PopVar[] =>
    (validPopVars[v] ?? []).filter(p => !excludedPop.has(p))

  const values = validValues[scenario].filter(v => {
    if (excludedVal.has(v)) return false
    const base = validPopVars[v]
    return !base || popVarsFor(v).length > 0
  })

  return { values, popVarsFor }
}
