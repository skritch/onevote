<script lang="ts">
  import { untrack } from "svelte";
  import { chartState } from "../lib/chartState.svelte.js";
  import { validPopVars, getValidForYear, scenarioNames } from "../lib/manifest.js";
  import type { Scenario, ValueType, PopVar } from "../lib/values.js";
  import ElectionPlot from "./ElectionPlot.svelte";
  import SettingsPanel from "./SettingsPanel.svelte";
  import Select from "./Select.svelte";

  let { years }: { years: number[] } = $props();

  let selectedYear = $state(
    untrack(() => {
      const now = new Date().getFullYear();
      return String(years.find((y) => y <= now) ?? years[0] ?? 2024);
    }),
  );

  $effect(() => {
    chartState.year = Number(selectedYear);
  });

  // Snap value/popVar to valid combo when year changes.
  // Using p2 constraints since it's the most permissive scenario on this page.
  // p5 doesn't support 'pv' — if selected, the p5 chart will render empty bars.
  $effect(() => {
    const year = Number(selectedYear);
    const { values, popVarsFor } = getValidForYear(year, "p2");
    const curVal = untrack(() => chartState.value);
    const curPop = untrack(() => chartState.popVar);
    const nextVal = values.includes(curVal) ? curVal : (values[0] ?? "av");
    const pops = popVarsFor(nextVal);
    const nextPop =
      pops.length === 0 || pops.includes(curPop) ? curPop : pops[0];
    if (nextVal !== curVal) chartState.value = nextVal;
    if (nextPop !== curPop) chartState.popVar = nextPop;
  });

  // Read URL params on mount
  $effect(() => {
    const params = new URLSearchParams(window.location.search);
    const year = params.get("year");
    if (year && years.includes(Number(year))) selectedYear = year;
    const valueParam = params.get("value");
    if (valueParam && valueParam in validPopVars)
      chartState.value = valueParam as ValueType;
    const popParam = params.get("pop");
    if (popParam) chartState.popVar = popParam as PopVar;
    const sortParam = params.get("sort");
    if (sortParam === "alpha" || sortParam === "value")
      chartState.sort = sortParam;
  });

  // Write URL on change
  let urlSyncReady = false;
  $effect(() => {
    void [selectedYear, chartState.value, chartState.popVar, chartState.sort];
    if (!urlSyncReady) {
      urlSyncReady = true;
      return;
    }
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.set("year", selectedYear);
    newUrl.searchParams.set("value", chartState.value);
    if (chartState.popVar) newUrl.searchParams.set("pop", chartState.popVar);
    if (chartState.sort !== "alpha")
      newUrl.searchParams.set("sort", chartState.sort);
    else newUrl.searchParams.delete("sort");
    window.history.replaceState({}, "", newUrl);
  });

  const showPopVar = $derived(
    (validPopVars[chartState.value] ?? []).length > 0,
  );

  // TODO: office picker — all scenarios here are presidential;
  // add office selector when senate/house scenario data is available.

  const SCENARIOS: Scenario[] = ["p2", "p1", "p5"];
</script>

<div class="content-page scenarios-page">
  <div class="page-header">
    <div class="page-controls">
      <Select
        bind:value={selectedYear}
        options={years.map((y) => ({ value: String(y), label: String(y) }))}
      />
      <SettingsPanel showScenario={false} />
    </div>
  </div>

  {#each SCENARIOS as scenario}
    <section class="scenario-section">
      <h3 class="scenario-title">{scenarioNames[scenario]}</h3>
      <ElectionPlot
        {scenario}
        year={chartState.year}
        value={chartState.value}
        popVar={showPopVar ? chartState.popVar : undefined}
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
