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

export const scenarioDescriptions: Record<Scenario, string> = {
  p1: 'All votes are pooled nationally; the candidate with the most total votes wins. No Electoral College.',
  p2: 'Each state awards its electors votes to its popular-vote winner. This is nearly identical to the present-day system, but omits the idiosyncrasies of Maine and Nebraska',
  // p3: 'The present-day. Most states award all electoral votes to their popular-vote winner, while Maine and Nebraska award one elector to the winner of each House district, and the remaining two "Senate" electors to the statewide popular-vote winner.
  // p4: 'All states award electors to the popular winner in each House district, and the remaining two "Senate" electors to the statewide popular-vote winner. This is the system used by Maine and Nebraska at present, but applied to all states.
  p5: "Each state's electoral votes are split among all candidates in proportion to their share of the popular vote in that state.",
}

export const valueDescriptions: Record<ValueType, string> = {
  av: 'Electors per voter, scaled to have a nationwide average of 1.00.',
  pv: 'The approximate fraction of all possible election outcomes in which this voter decides the overall election, scaled to have a nationwide average of 1.00.',
  wvv: 'Electors per winning-party voter, scaled to have a nationwide average of 1.00.',
}

export const popVarDescriptions: Record<PopVar, string> = {
  ap: 'The official U.S. Census population count used to apportion House seats and Electoral College votes. Includes all residents regardless of citizenship or voting eligibility.',
  vap: 'Estimated number of residents age 18 and older. Includes non-citizens and those legally barred from voting.',
  vep: 'Estimated number of citizens age 18 or older who are legally eligible to vote in federal elections.',
  vp: 'The actual number of ballots cast in the election.',
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
