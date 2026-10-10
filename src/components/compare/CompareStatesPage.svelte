<script module lang="ts">
  import { displayScenarios } from "../../lib/manifest.js";
  import type { ValueType, PopVar, Scenario } from "../../lib/values.js";

  export type CompareStatesParams = {
    state1: string;
    district1: string;
    party1: string;
    state2: string;
    district2: string;
    party2: string;
    year: number;
    office: string;
    value: ValueType;
    popVar: PopVar;
    scenario: Scenario;
  };

  export const defaultCompareStatesParams: CompareStatesParams = {
    state1: "",
    district1: "",
    party1: "",
    state2: "",
    district2: "",
    party2: "",
    year: 2024,
    office: "president",
    value: "av" as ValueType,
    popVar: "ap" as PopVar,
    scenario: displayScenarios[0],
  };
</script>

<script lang="ts">
  import { readFromUrl, syncToUrl } from "../../utils/url.js";
  import type { State } from "../../lib/states.js";
  import type { StatePO } from "../../lib/states.js";
  import type { DistrictIndex } from "../../lib/districts.js";
  import CompareStatesControls from "./CompareStatesControls.svelte";
  import StateValueCard from "../StateValueCard.svelte";
  import StateFactBox from "../StateFactBox.svelte";
  import ElectionPlot from "../ElectionPlot.svelte";
  import type { Party } from "../../lib/party.js";
  import type { Office } from "../../lib/elections.js";
  import { validPopVars } from "../../lib/manifest.js";

  type Props = {
    years: number[];
    states: State[];
    districtIndex: Record<string, DistrictIndex>;
  };

  let { years, states, districtIndex }: Props = $props();

  let params = $state<CompareStatesParams>(
    typeof window !== "undefined"
      ? readFromUrl(new URLSearchParams(window.location.search), defaultCompareStatesParams)
      : { ...defaultCompareStatesParams },
  );

  let urlSyncReady = false;
  $effect(() => {
    void [
      params.state1, params.district1, params.party1,
      params.state2, params.district2, params.party2,
      params.year, params.office, params.value, params.popVar, params.scenario,
    ];
    if (!urlSyncReady) { urlSyncReady = true; return; }
    const newUrl = new URL(window.location.href);
    syncToUrl(params, defaultCompareStatesParams, newUrl);
    window.history.replaceState({}, "", newUrl);
  });

  const stateName1 = $derived(states.find((s) => s.statePO === params.state1)?.stateName ?? params.state1);
  const stateName2 = $derived(states.find((s) => s.statePO === params.state2)?.stateName ?? params.state2);

  // Snap popVar to first valid option when value changes (e.g. WVV only supports VP).
  $effect(() => {
    const validPops = (validPopVars[params.value] ?? []) as PopVar[];
    if (validPops.length > 0 && !validPops.includes(params.popVar as PopVar)) {
      params.popVar = validPops[0];
    }
  });

  const effectivePopVar = $derived(
    (validPopVars[params.value] ?? []).length > 0 ? params.popVar : undefined,
  );

  const focusStates = $derived(
    [params.state1, params.state2].filter(Boolean) as StatePO[],
  );
</script>

<CompareStatesControls {years} {states} {districtIndex} bind:params={params} />

{#if params.state1 && params.state2}
  <div class="results-panel">
    <div class="cards-row">
      <StateValueCard
        stateName={stateName1}
        statePO={params.state1 as StatePO}
        scenario={params.scenario}
        year={params.year}
        office={params.office as Office}
        value={params.value}
        popVar={params.popVar}
        party={params.party1 as Party | undefined}
        district={params.district1 || undefined}
        districtId={params.district1 || undefined}
      />
      <StateValueCard
        stateName={stateName2}
        statePO={params.state2 as StatePO}
        scenario={params.scenario}
        year={params.year}
        office={params.office as Office}
        value={params.value}
        popVar={params.popVar}
        party={params.party2 as Party | undefined}
        district={params.district2 || undefined}
        districtId={params.district2 || undefined}
      />
    </div>

    <div class="cards-row">
      <StateFactBox
        statePO={params.state1 as StatePO}
        districtIndex={districtIndex[params.state1] ?? null}
        year={params.year}
        districtId={params.district1 || undefined}
        onDistrictChange={(id) => { params.district1 = id ?? ""; }}
      />
      <StateFactBox
        statePO={params.state2 as StatePO}
        districtIndex={districtIndex[params.state2] ?? null}
        year={params.year}
        districtId={params.district2 || undefined}
        onDistrictChange={(id) => { params.district2 = id ?? ""; }}
      />
    </div>

    <div class="plot-row">
      <ElectionPlot
        scenario={params.scenario}
        year={params.year}
        focusStatePO={focusStates}
        value={params.value}
        popVar={effectivePopVar}
      />
    </div>
  </div>
{/if}

<style lang="scss">
  @use "../../styles/variables.scss";

  .results-panel {
    display: flex;
    flex-direction: column;
    gap: variables.$spacing-lg;
  }

  .cards-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: variables.$spacing-md;

    @media (max-width: 600px) {
      grid-template-columns: 1fr;
    }
  }

  .plot-row {
    width: 100%;
  }
</style>
