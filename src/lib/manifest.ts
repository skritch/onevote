import type { Scenario, ValueType, PopVar } from './values.js'


export type Year = number
export const YEARS: Year[] = [1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024, 2028]

export type YearConstraint = {
  years?: Year[]
  before?: Year    // applies if year < before
  from?: Year      // applies if year >= from
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
  vp: 'Voting Population',
}

export const popVarShortNames: Record<PopVar, string> = {
  ap: 'AP',
  vap: 'VAP',
  vep: 'VEP',
  vp: 'VP',
}

export const displayScenarios: Scenario[] = ["p3", "p1", "p4", "p5"];

export const scenarioNames: Record<Scenario, string> = {
  p1: 'National General Election',
  p2: 'Simplified Electoral College',
  p3: 'Electoral College',
  p4: 'Districtized Electoral College',
  p5: 'Proportional Electoral College',
}

export const scenarioShortNames: Record<Scenario, string> = {
  p1: 'NGE',
  p2: 'SEC',
  p3: 'EC',
  p4: 'DEC',
  p5: 'PEC',
}

export const scenarioDescriptions: Record<Scenario, string> = {
  p1: 'All votes are pooled nationally; the candidate with the most total votes wins. No Electoral College.',
  p2: 'Each state awards its electors votes to its popular-vote winner. This is nearly identical to the present-day system, but omits the idiosyncrasies of Maine and Nebraska.',
  p3: 'The present-day system. Most states award all electoral votes to their popular-vote winner, while Maine and Nebraska award one elector to the winner of each congressional district, plus two statewide "Senate" electors.',
  p4: 'All states award an elector to the popular-vote winner in each congressional district, and award their two "Senate" electors to the statewide popular vote winner. This applies the system currently used in Maine and Nebraska nationwide.',
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
  p3: ['av', 'pv', 'wvv'],
  p4: ['av', 'pv', 'wvv'],
  p5: ['av', 'wvv'],
}

// Pop vars excluded per scenario regardless of year.
// p3/p4 use district-level apportionment data which lacks VEP estimates.
export const scenarioExcludedPopVars: Partial<Record<Scenario, PopVar[]>> = {
  p3: ['vep'],
  p4: ['vep'],
}

// Per-year restrictions applied on top of scenario-based ones.
// av+ap is always the fallback — constraints here must never exclude both.
export const yearConstraints: YearConstraint[] = [
  // 2028 has no vote results and only AP, so PV and WVV are unavailable
  { years: [2028], excludePopVars: ['vap', 'vep', 'vp'], excludeValues: ['pv', 'wvv'] },
  // 1976 is missing VAP/VEP data
  { years: [1976], excludePopVars: ['vap', 'vep'] },
  // p4 requires district data (only from 2012); p3 still works at state level pre-2012
  { before: 2012, excludeScenarios: ['p4'] },
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

  scenarioExcludedPopVars[scenario]?.forEach(p => excludedPop.add(p))

  const popVarsFor = (v: ValueType): PopVar[] =>
    (validPopVars[v] ?? []).filter(p => !excludedPop.has(p))

  const values = validValues[scenario].filter(v => {
    if (excludedVal.has(v)) return false
    const base = validPopVars[v]
    return !base || popVarsFor(v).length > 0
  })

  return { values, popVarsFor }
}
