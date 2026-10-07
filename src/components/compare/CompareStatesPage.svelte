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
  import type { DistrictIndex } from "../../lib/districts.js";
  import CompareStatesControls from "./CompareStatesControls.svelte";

  type Props = {
    years: number[];
    states: State[];
    districtIndex: Record<string, DistrictIndex>;
  };

  let { years, states, districtIndex }: Props = $props();

  const params = $state<CompareStatesParams>(
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

</script>

<CompareStatesControls {years} {states} {districtIndex} {params} />

<div class="results-panel">
  <!-- results will go here -->
</div>

<style lang="scss">
  .results-panel {
    min-height: 300px;
  }
</style>
