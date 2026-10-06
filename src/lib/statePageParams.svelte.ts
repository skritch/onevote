import type { ValueType, PopVar, Scenario } from './values.js'
import type { Office } from './elections.js'
import type { Party } from './party.js'


export type SortMode = 'value' | 'alpha'

type StatePageParams = {
  scenario: Scenario,
  year: number,
  office: Office,
  value: ValueType,
  popVar: PopVar,
  sort: SortMode,
  party?: Party,
  district?: string,
  districtId?: string
}

const defaultParams = {
  scenario: 'p2' as Scenario,
  year: 2024,
  office: 'president' as Office,
  value: 'av' as ValueType,
  popVar: 'ap' as PopVar,
  sort: 'alpha' as SortMode,
  party: '' as Party,
  district: '' as string,
  districtId: '' as string,
}

export const statePageParams = $state<StatePageParams>(defaultParams)
