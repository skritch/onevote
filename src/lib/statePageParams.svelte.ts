import type { ValueType, PopVar, Scenario } from './values.js'
import { OFFICES, officesByName, type Office } from './elections.js'
import { PARTIES, type Party } from './party.js'
import { scenarioNames, valueNames, popVarNames } from './manifest.js'


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

export const defaultStatePageParams = {
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

export const statePageParams = $state<StatePageParams>(defaultStatePageParams)



export function fromUrlParams(urlParams: URLSearchParams): StatePageParams {

  const builder: Partial<StatePageParams> = defaultStatePageParams

  const [yearParam, officeParam] = urlParams.get("election")?.split("-") ?? [null, null]
  const year = parseInt(yearParam ?? '', 10)
  // TODO: is valid year
  if (!isNaN(year) && year !== defaultStatePageParams.year) { builder.year = year }
  if (officeParam
    && OFFICES.includes(officeParam as Office)
    && officeParam !== defaultStatePageParams.office) { builder.office = officeParam as Office }

  const scenarioParam = urlParams.get("scenario");
  if (scenarioParam && Object.keys(scenarioNames).includes(scenarioParam as Scenario)) {
    builder.scenario = scenarioParam as Scenario
  }

  const valueParam = urlParams.get("value");
  if (valueParam && Object.keys(valueNames).includes(valueParam as ValueType)) {
    builder.value = valueParam as ValueType
  }

  const popParam = urlParams.get("pop");
  if (popParam && Object.keys(popVarNames).includes(popParam as PopVar)) {
    builder.popVar = popParam as PopVar
  }

  const sortParam = urlParams.get("sort");
  if (sortParam === 'alpha' || sortParam === 'value') {
    builder.sort = sortParam
  }

  const partyParam = urlParams.get("party");
  if (partyParam && PARTIES.includes(partyParam as Party)) {
    builder.party = partyParam as Party
  }

  const districtParam = urlParams.get("district");
  if (districtParam) builder.district = districtParam

  const districtIdParam = urlParams.get("districtId");
  if (districtIdParam) builder.districtId = districtIdParam

  return builder as StatePageParams
}