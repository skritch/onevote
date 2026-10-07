<script module lang="ts">
  import type { ValueType, PopVar } from "../lib/values.js";

  export type ScenariosPageParams = {
    year: number;
    value: ValueType;
    popVar: PopVar;
    sort: "alpha" | "value";
  };

  export const defaultScenariosPageParams: ScenariosPageParams = {
    year: 2024,
    value: "av",
    popVar: "ap",
    sort: "alpha",
  };
</script>

<script lang="ts">
  import { untrack } from "svelte";
  import { getValidForYear, scenarioNames, displayScenarios } from "../lib/manifest.js";
  import type { Scenario } from "../lib/values.js";
  import { readFromUrl, syncToUrl } from "../utils/url.js";
  import ElectionPlot from "./ElectionPlot.svelte";
  import SettingsPanel from "./SettingsPanel.svelte";
  import Select from "./Select.svelte";

  let { years }: { years: number[] } = $props();

  // Dynamic year default: most recent non-future year in the data.
  const _defaults = untrack(() => ({
    ...defaultScenariosPageParams,
    year: years.find((y) => y <= new Date().getFullYear()) ?? years[0] ?? 2024,
  }));

  const params = $state<ScenariosPageParams>(
    typeof window !== "undefined"
      ? readFromUrl(new URLSearchParams(window.location.search), _defaults)
      : { ..._defaults },
  );

  // Snap value/popVar to valid combo when year changes.
  // Using p2 constraints since it's the most permissive scenario on this page.
  $effect(() => {
    const { values, popVarsFor } = getValidForYear(params.year, "p2");
    const curVal = untrack(() => params.value);
    const curPop = untrack(() => params.popVar);
    const nextVal = values.includes(curVal) ? curVal : (values[0] ?? "av");
    const pops = popVarsFor(nextVal);
    const nextPop = pops.length === 0 || pops.includes(curPop) ? curPop : pops[0];
    if (nextVal !== curVal) params.value = nextVal;
    if (nextPop !== curPop) params.popVar = nextPop;
  });

  // Write URL whenever relevant state changes (skip first run).
  let urlSyncReady = false;
  $effect(() => {
    void [params.year, params.value, params.popVar, params.sort];
    if (!urlSyncReady) { urlSyncReady = true; return; }
    const newUrl = new URL(window.location.href);
    syncToUrl(params, _defaults, newUrl);
    window.history.replaceState({}, "", newUrl);
  });

  const SCENARIOS = displayScenarios;
</script>

<div class="content-page scenarios-page">
  <div class="page-header">
    <div class="page-controls">
      <Select
        bind:value={params.year}
        options={years.map((y) => ({ value: y, label: String(y) }))}
      />
      <SettingsPanel
        showScenario={false}
        year={params.year}
        bind:value={params.value}
        bind:popVar={params.popVar}
      />
    </div>
  </div>

  {#each SCENARIOS as scenario}
    <section class="scenario-section">
      <h3 class="scenario-title">{scenarioNames[scenario]}</h3>
      <ElectionPlot
        {scenario}
        year={params.year}
        value={params.value}
        popVar={params.popVar}
        bind:sort={params.sort}
      />
      <div class="metrics-gap">
        <!-- TODO: show outcome metrics here — did this scenario flip the national winner?
             Which states gained / lost the most relative power vs. p2? -->
        <!-- TODO: party filter — shade bars by whether the state flipped under this scenario -->
        <!-- TODO: district breakdown for ME/NE when p3/p4 data is available -->
      </div>
    </section>
  {/each}

  <!-- TODO: essay section — elections where scenario choice changed the outcome
       (2000, 2016, others); discuss tradeoffs between equal-vote and existing EC -->
</div>

<style lang="scss">
  @use "../styles/variables.scss";

  .scenarios-page {
    display: flex;
    flex-direction: column;
    gap: variables.$spacing-lg;
  }

  .scenario-section {
    display: flex;
    flex-direction: column;
    gap: variables.$spacing-sm;
  }

  .scenario-title {
    font-size: 1rem;
    font-weight: 600;
    color: variables.$dark-gray;
    margin: 0;
  }

  .metrics-gap {
    min-height: 3rem;
  }
</style>
