<script lang="ts">
  import { untrack } from "svelte";
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
  const year = $derived(Number(selectedYear));

  let value = $state<ValueType>("av");
  let popVar = $state<PopVar>("ap");
  let sort = $state<"alpha" | "value">("alpha");

  // Snap value/popVar to valid combo when year changes.
  // Using p2 constraints since it's the most permissive scenario on this page.
  // p5 doesn't support 'pv' — if selected, the p5 chart will render empty bars.
  $effect(() => {
    const { values, popVarsFor } = getValidForYear(year, "p2");
    const curVal = untrack(() => value);
    const curPop = untrack(() => popVar);
    const nextVal = values.includes(curVal) ? curVal : (values[0] ?? "av");
    const pops = popVarsFor(nextVal);
    const nextPop =
      pops.length === 0 || pops.includes(curPop) ? curPop : pops[0];
    if (nextVal !== curVal) value = nextVal;
    if (nextPop !== curPop) popVar = nextPop;
  });

  // Read URL params on mount
  $effect(() => {
    const params = new URLSearchParams(window.location.search);
    const yearParam = params.get("year");
    if (yearParam && years.includes(Number(yearParam))) selectedYear = yearParam;
    const valueParam = params.get("value");
    if (valueParam && valueParam in validPopVars) value = valueParam as ValueType;
    const popParam = params.get("pop");
    if (popParam) popVar = popParam as PopVar;
    const sortParam = params.get("sort");
    if (sortParam === "alpha" || sortParam === "value") sort = sortParam;
  });

  // Write URL on change
  let urlSyncReady = false;
  $effect(() => {
    void [selectedYear, value, popVar, sort];
    if (!urlSyncReady) {
      urlSyncReady = true;
      return;
    }
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.set("year", selectedYear);
    newUrl.searchParams.set("value", value);
    if (popVar) newUrl.searchParams.set("pop", popVar);
    if (sort !== "alpha") newUrl.searchParams.set("sort", sort);
    else newUrl.searchParams.delete("sort");
    window.history.replaceState({}, "", newUrl);
  });

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
      <SettingsPanel
        showScenario={false}
        {year}
        bind:value
        bind:popVar
      />
    </div>
  </div>

  {#each SCENARIOS as scenario}
    <section class="scenario-section">
      <h3 class="scenario-title">{scenarioNames[scenario]}</h3>
      <ElectionPlot
        {scenario}
        {year}
        {value}
        {popVar}
        bind:sort
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
