import type { Scenario, ValueType, PopVar } from './values.js'

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

// Pop vars applicable per value type. wvv has none.
export const validPopVars: Partial<Record<ValueType, PopVar[]>> = {
  av: ['ap', 'vap', 'vep', 'vp'],
  pv: ['vap', 'vep', 'vp'],
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
