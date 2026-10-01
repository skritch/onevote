<script lang="ts">
  import { untrack } from 'svelte';
  import { chartState } from '../../lib/chartState.svelte.js';
  import {
    valueNames,
    popVarNames,
    defaultValue,
    defaultPopVar,
    getValidForYear,
  } from '../../lib/manifest.js';
  import type { ValueType, PopVar, Scenario } from '../../lib/values.js';

  let { year }: { year: number } = $props();

  // Parse URL params synchronously so initial state is correct on first render
  const _urlParams =
    typeof window !== 'undefined'
      ? new URLSearchParams(window.location.search)
      : null;

  if (_urlParams) {
    const scenarioParam = _urlParams.get('scenario');
    if (scenarioParam === 'p1' || scenarioParam === 'p2' || scenarioParam === 'p5')
      chartState.scenario = scenarioParam as Scenario;
    const valueParam = _urlParams.get('value');
    if (valueParam && valueParam in valueNames) chartState.value = valueParam as ValueType;
    const popParam = _urlParams.get('pop');
    if (popParam && popParam in popVarNames) chartState.popVar = popParam as PopVar;
    const sortParam = _urlParams.get('sort');
    if (sortParam === 'alpha' || sortParam === 'value') chartState.sort = sortParam;
  }

  // Fix year and office immediately
  chartState.year = year;
  chartState.office = 'president';

  // Snap value/popVar to a valid combo when scenario changes (year is fixed)
  $effect(() => {
    chartState.year = year;
    const { values, popVarsFor } = getValidForYear(year, chartState.scenario);
    const curVal = untrack(() => chartState.value);
    const curPop = untrack(() => chartState.popVar);
    const nextVal = values.includes(curVal) ? curVal : (values[0] ?? 'av');
    const pops = popVarsFor(nextVal);
    const nextPop = pops.length === 0 || pops.includes(curPop) ? curPop : pops[0];
    if (nextVal !== curVal) chartState.value = nextVal;
    if (nextPop !== curPop) chartState.popVar = nextPop;
  });

  // Reveal sections hidden by [data-election-loading]
  $effect(() => {
    document.documentElement.removeAttribute('data-election-loading');
  });

  // Write URL whenever relevant state changes
  let urlSyncReady = false;
  let settingsWritten = false;
  $effect(() => {
    void [chartState.scenario, chartState.value, chartState.popVar, chartState.sort];
    if (!urlSyncReady) { urlSyncReady = true; return; }
    syncURL();
  });

  function syncURL() {
    const newUrl = new URL(window.location.href);

    if (chartState.scenario !== 'p2') newUrl.searchParams.set('scenario', chartState.scenario);
    else newUrl.searchParams.delete('scenario');

    const defPop = defaultPopVar[chartState.value];
    const hasNonDefault =
      chartState.value !== defaultValue ||
      (defPop != null && chartState.popVar !== defPop) ||
      chartState.sort !== 'alpha';
    if (hasNonDefault) settingsWritten = true;

    if (settingsWritten) {
      newUrl.searchParams.set('value', chartState.value);
      if (defPop != null) newUrl.searchParams.set('pop', chartState.popVar);
      else newUrl.searchParams.delete('pop');
      if (chartState.sort !== 'alpha') newUrl.searchParams.set('sort', chartState.sort);
      else newUrl.searchParams.delete('sort');
    } else {
      newUrl.searchParams.delete('value');
      newUrl.searchParams.delete('pop');
      newUrl.searchParams.delete('sort');
    }

    window.history.replaceState({}, '', newUrl);
  }
</script>
