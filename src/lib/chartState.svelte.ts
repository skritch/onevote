import type { ValueType, PopVar, Scenario } from './values.js'
import type { Office } from './elections.js'

export type SortMode = 'value' | 'alpha'

export const chartState = $state({
  scenario: 'p2' as Scenario,
  year: 2024,
  office: 'president' as Office,
  value: 'av' as ValueType,
  popVar: 'ap' as PopVar,
  sort: 'alpha' as SortMode,
  party: '' as string,
  district: '' as string,
  districtId: '' as string,
})
