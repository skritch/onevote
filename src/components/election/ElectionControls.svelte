<script lang="ts">
  import { untrack } from "svelte";
  import { statePageParams } from "../../lib/statePageParams.svelte.js";
  import {
    valueNames,
    popVarNames,
    defaultValue,
    defaultPopVar,
    getValidForYear,
  } from "../../lib/manifest.js";
  import type { ValueType, PopVar, Scenario } from "../../lib/values.js";

  let { year }: { year: number } = $props();

  // Parse URL params synchronously so initial state is correct on first render
  const _urlParams =
    typeof window !== "undefined"
      ? new URLSearchParams(window.location.search)
      : null;

  if (_urlParams) {
    const scenarioParam = _urlParams.get("scenario");
    if (
      scenarioParam === "p1" ||
      scenarioParam === "p2" ||
      scenarioParam === "p5"
    )
      statePageParams.scenario = scenarioParam as Scenario;
    const valueParam = _urlParams.get("value");
    if (valueParam && valueParam in valueNames)
      statePageParams.value = valueParam as ValueType;
    const popParam = _urlParams.get("pop");
    if (popParam && popParam in popVarNames)
      statePageParams.popVar = popParam as PopVar;
    const sortParam = _urlParams.get("sort");
    if (sortParam === "alpha" || sortParam === "value")
      statePageParams.sort = sortParam;
  }

  // Fix year and office immediately
  statePageParams.year = year;
  statePageParams.office = "president";

  // Snap value/popVar to a valid combo when scenario changes (year is fixed)
  $effect(() => {
    statePageParams.year = year;
    const { values, popVarsFor } = getValidForYear(
      year,
      statePageParams.scenario,
    );
    const curVal = untrack(() => statePageParams.value);
    const curPop = untrack(() => statePageParams.popVar);
    const nextVal = values.includes(curVal) ? curVal : (values[0] ?? "av");
    const pops = popVarsFor(nextVal);
    const nextPop =
      pops.length === 0 || pops.includes(curPop) ? curPop : pops[0];
    if (nextVal !== curVal) statePageParams.value = nextVal;
    if (nextPop !== curPop) statePageParams.popVar = nextPop;
  });

  // Reveal sections hidden by [data-election-loading]
  $effect(() => {
    document.documentElement.removeAttribute("data-election-loading");
  });

  // Write URL whenever relevant state changes
  let urlSyncReady = false;
  let settingsWritten = false;
  $effect(() => {
    void [
      statePageParams.scenario,
      statePageParams.value,
      statePageParams.popVar,
      statePageParams.sort,
    ];
    if (!urlSyncReady) {
      urlSyncReady = true;
      return;
    }
    syncURL();
  });

  function syncURL() {
    const newUrl = new URL(window.location.href);

    if (statePageParams.scenario !== "p2")
      newUrl.searchParams.set("scenario", statePageParams.scenario);
    else newUrl.searchParams.delete("scenario");

    const defPop = defaultPopVar[statePageParams.value];
    const hasNonDefault =
      statePageParams.value !== defaultValue ||
      (defPop != null && statePageParams.popVar !== defPop) ||
      statePageParams.sort !== "alpha";
    if (hasNonDefault) settingsWritten = true;

    if (settingsWritten) {
      newUrl.searchParams.set("value", statePageParams.value);
      if (defPop != null)
        newUrl.searchParams.set("pop", statePageParams.popVar);
      else newUrl.searchParams.delete("pop");
      if (statePageParams.sort !== "alpha")
        newUrl.searchParams.set("sort", statePageParams.sort);
      else newUrl.searchParams.delete("sort");
    } else {
      newUrl.searchParams.delete("value");
      newUrl.searchParams.delete("pop");
      newUrl.searchParams.delete("sort");
    }

    window.history.replaceState({}, "", newUrl);
  }
</script>
