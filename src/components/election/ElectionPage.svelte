<script lang="ts">
  import { untrack } from "svelte";
  import { getValidForYear } from "../../lib/manifest.js";
  import type { Scenario, ValueType, PopVar } from "../../lib/values.js";
  import { readFromUrl, syncToUrl } from "../../utils/url.js";
  import SettingsPanel from "../SettingsPanel.svelte";
  import ElectionPlot from "../ElectionPlot.svelte";

  type Props = { year: number; electionName: string };
  let { year, electionName }: Props = $props();

  const _electionDefaults = {
    scenario: "p2" as Scenario,
    value: "av" as ValueType,
    popVar: "ap" as PopVar,
    sort: "alpha" as "alpha" | "value",
  };

  const _parsed =
    typeof window !== "undefined"
      ? readFromUrl(new URLSearchParams(window.location.search), _electionDefaults)
      : _electionDefaults;

  let scenario = $state(_parsed.scenario);
  let value = $state(_parsed.value);
  let popVar = $state(_parsed.popVar);
  let sort = $state(_parsed.sort);

  // Snap value/popVar to a valid combo when scenario changes (year is fixed)
  $effect(() => {
    const { values, popVarsFor } = getValidForYear(year, scenario);
    const curVal = untrack(() => value);
    const curPop = untrack(() => popVar);
    const nextVal = values.includes(curVal) ? curVal : (values[0] ?? "av");
    const pops = popVarsFor(nextVal);
    const nextPop =
      pops.length === 0 || pops.includes(curPop) ? curPop : pops[0];
    if (nextVal !== curVal) value = nextVal as ValueType;
    if (nextPop !== curPop) popVar = nextPop as PopVar;
  });

  // Reveal sections hidden by [data-election-loading]
  $effect(() => {
    document.documentElement.removeAttribute("data-election-loading");
  });

  // Write URL whenever relevant state changes (skip first run)
  let urlSyncReady = false;
  $effect(() => {
    void [scenario, value, popVar, sort];
    if (!urlSyncReady) { urlSyncReady = true; return; }
    const newUrl = new URL(window.location.href);
    syncToUrl({ scenario, value, popVar, sort }, _electionDefaults, newUrl);
    window.history.replaceState({}, "", newUrl);
  });
</script>

<div class="election-page">
  <div class="page-header election-page__header">
    <h1>{electionName}</h1>
    <div class="page-controls">
      <SettingsPanel
        {year}
        bind:scenario
        bind:value
        bind:popVar
      />
    </div>
  </div>

  <div class="content-page">
    <div class="election-page__chart">
      <ElectionPlot
        focusStatePO=""
        {scenario}
        {year}
        {value}
        {popVar}
        bind:sort
      />
    </div>
  </div>
</div>

<style lang="scss">
  @use "../../styles/variables.scss";

  .election-page {
    h1 {
      font-size: variables.$font-size-large;
      color: variables.$dark-gray;
      margin: 0;
      white-space: nowrap;
    }

    &__header {
      margin-bottom: variables.$spacing-md;
    }

    &__chart {
      @include variables.card;
      padding: variables.$spacing-sm variables.$spacing-md;
    }
  }

  :global([data-election-loading] .page-controls),
  :global([data-election-loading] .election-page__chart) {
    opacity: 0;
  }
</style>
