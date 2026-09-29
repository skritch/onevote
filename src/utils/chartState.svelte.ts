import type { ValueType, PopVar, Scenario } from './values.js'

export const chartState = $state({
  scenario: 'p2' as Scenario,
  year: 2024,
  value: 'av' as ValueType,
  popVar: 'ap' as PopVar,
})
