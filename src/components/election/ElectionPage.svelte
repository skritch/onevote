<script lang="ts">
  import { untrack } from "svelte";
  import {
    valueNames,
    popVarNames,
    defaultValue,
    defaultPopVar,
    getValidForYear,
  } from "../../lib/manifest.js";
  import type { Scenario, ValueType, PopVar } from "../../lib/values.js";
  import SettingsPanel from "../SettingsPanel.svelte";
  import ElectionPlot from "../ElectionPlot.svelte";

  type Props = { year: number; electionName: string };
  let { year, electionName }: Props = $props();

  // Parse URL params synchronously so initial state is correct on first render
  const _urlParams =
    typeof window !== "undefined"
      ? new URLSearchParams(window.location.search)
      : null;

  function initFromUrl<T extends string>(
    param: string | null,
    guard: (v: string) => v is T,
    fallback: T,
  ): T {
    return param && guard(param) ? param : fallback;
  }

  const _scenario = _urlParams?.get("scenario") ?? null;
  const _value = _urlParams?.get("value") ?? null;
  const _pop = _urlParams?.get("pop") ?? null;
  const _sort = _urlParams?.get("sort") ?? null;

  let scenario = $state<Scenario>(
    initFromUrl(_scenario, (v): v is Scenario => v === "p1" || v === "p2" || v === "p5", "p2"),
  );
  let value = $state<ValueType>(
    initFromUrl(_value, (v): v is ValueType => v in valueNames, "av" as ValueType),
  );
  let popVar = $state<PopVar>(
    initFromUrl(_pop, (v): v is PopVar => v in popVarNames, "ap" as PopVar),
  );
  let sort = $state<"alpha" | "value">(
    initFromUrl(_sort, (v): v is "alpha" | "value" => v === "alpha" || v === "value", "alpha"),
  );

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
  let settingsWritten = false;
  $effect(() => {
    void [scenario, value, popVar, sort];
    if (!urlSyncReady) {
      urlSyncReady = true;
      return;
    }
    syncURL();
  });

  function syncURL() {
    const newUrl = new URL(window.location.href);

    if (scenario !== "p2") newUrl.searchParams.set("scenario", scenario);
    else newUrl.searchParams.delete("scenario");

    const defPop = defaultPopVar[value];
    const hasNonDefault =
      value !== defaultValue ||
      (defPop != null && popVar !== defPop) ||
      sort !== "alpha";
    if (hasNonDefault) settingsWritten = true;

    if (settingsWritten) {
      newUrl.searchParams.set("value", value);
      if (defPop != null) newUrl.searchParams.set("pop", popVar);
      else newUrl.searchParams.delete("pop");
      if (sort !== "alpha") newUrl.searchParams.set("sort", sort);
      else newUrl.searchParams.delete("sort");
    } else {
      newUrl.searchParams.delete("value");
      newUrl.searchParams.delete("pop");
      newUrl.searchParams.delete("sort");
    }

    window.history.replaceState({}, "", newUrl);
  }
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
