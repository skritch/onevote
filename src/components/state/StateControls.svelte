<script lang="ts">
  import { untrack } from "svelte";
  import { officesByName } from "../../lib/elections";
  import { chartState } from "../../lib/chartState.svelte.js";
  import { valueNames, popVarNames, defaultValue, defaultPopVar, getValidForYear } from '../../lib/manifest.js';
  import type { ValueType, PopVar, Scenario } from '../../lib/values.js';

  let {
    years,
    offices,
  }: {
    years: number[];
    offices: string[];
  } = $props();

  let yearDropdownOpen = $state(false);
  let yearDropdownEl: HTMLElement | null = $state(null);

  function handleWindowClick(event: MouseEvent) {
    if (yearDropdownEl && !yearDropdownEl.contains(event.target as Node)) {
      yearDropdownOpen = false;
      document.dispatchEvent(new CustomEvent('ui:close'));
    }
  }

  const parties = ["Democrat", "Republican", "Other"];

  // Parse URL params synchronously so initial state is correct on first render
  const _urlParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
  const _election = _urlParams?.get("election") ?? null;
  const [_yearParam, _officeParam] = _election ? _election.split("-") : [null, null];

  // Apply chartState fields from URL before effects run
  if (_urlParams) {
    const scenarioParam = _urlParams.get("scenario");
    if (scenarioParam === 'p1' || scenarioParam === 'p2' || scenarioParam === 'p5')
      chartState.scenario = scenarioParam as Scenario;
    const valueParam = _urlParams.get("value");
    if (valueParam && valueParam in valueNames) chartState.value = valueParam as ValueType;
    const popParam = _urlParams.get("pop");
    if (popParam && popParam in popVarNames) chartState.popVar = popParam as PopVar;
    const sortParam = _urlParams.get("sort");
    if (sortParam === 'alpha' || sortParam === 'value') chartState.sort = sortParam;
  }

  const _initialYear = (() => {
    if (_yearParam && years.includes(Number(_yearParam))) return _yearParam;
    const now = new Date().getFullYear();
    return String(years.find(y => y <= now) ?? years[0] ?? 2024);
  })();
  const _initialOffice = (() => {
    if (_officeParam) {
      const displayName = Object.entries(officesByName).find(([, v]) => v === _officeParam)?.[0];
      if (displayName) return displayName;
    }
    return offices[0] ?? "";
  })();
  const _partyParam = _urlParams?.get("party") ?? null;

  let selectedYear = $state(_initialYear);
  let selectedOffice = $state(_initialOffice);
  let selectedParty = $state(_partyParam ? (parties.find(p => p.toLowerCase() === _partyParam.toLowerCase()) ?? "") : "");

  // Sync local selectors → chartState
  $effect(() => { chartState.year = Number(selectedYear) });
  $effect(() => { chartState.office = officesByName[selectedOffice] ?? 'president' });
  $effect(() => { chartState.party = selectedParty });

  // Snap value/popVar to a valid combo when year or scenario changes
  $effect(() => {
    const year = Number(selectedYear)
    const { values, popVarsFor } = getValidForYear(year, chartState.scenario)
    const curVal = untrack(() => chartState.value)
    const curPop = untrack(() => chartState.popVar)
    const nextVal = values.includes(curVal) ? curVal : (values[0] ?? 'av')
    const pops = popVarsFor(nextVal)
    const nextPop = pops.length === 0 || pops.includes(curPop) ? curPop : pops[0]
    if (nextVal !== curVal) chartState.value = nextVal
    if (nextPop !== curPop) chartState.popVar = nextPop
  });

  // Reveal page sections hidden by [data-state-loading] once correct values are applied.
  $effect(() => {
    document.documentElement.removeAttribute('data-state-loading');
  });

  // Write URL whenever any relevant state changes (skip first run to let URL read happen first)
  let urlSyncReady = false;
  // Once any non-default setting has appeared, always write all settings (even if reverted to default)
  let settingsWritten = false;
  $effect(() => {
    void [selectedYear, selectedOffice, selectedParty, chartState.scenario, chartState.value, chartState.popVar, chartState.sort];
    if (!urlSyncReady) { urlSyncReady = true; return; }
    syncURL();
  });

  function syncURL() {
    const officeKey = officesByName[selectedOffice] ?? "president";
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.set("election", `${selectedYear}-${officeKey}`);

    if (selectedParty) newUrl.searchParams.set("party", selectedParty);
    else newUrl.searchParams.delete("party");

    if (chartState.scenario !== 'p2') newUrl.searchParams.set("scenario", chartState.scenario);
    else newUrl.searchParams.delete("scenario");

    const defPop = defaultPopVar[chartState.value];
    const hasNonDefault = chartState.value !== defaultValue ||
      (defPop != null && chartState.popVar !== defPop) ||
      chartState.sort !== 'alpha';
    if (hasNonDefault) settingsWritten = true;

    if (settingsWritten) {
      newUrl.searchParams.set("value", chartState.value);
      if (defPop != null) newUrl.searchParams.set("pop", chartState.popVar);
      else newUrl.searchParams.delete("pop");
      if (chartState.sort !== 'alpha') newUrl.searchParams.set("sort", chartState.sort);
      else newUrl.searchParams.delete("sort");
    } else {
      newUrl.searchParams.delete("value");
      newUrl.searchParams.delete("pop");
      newUrl.searchParams.delete("sort");
    }

    window.history.replaceState({}, "", newUrl);
  }
</script>

<svelte:window onclick={handleWindowClick} />

<div class="state-page__controls">
  <span class="select-wrapper select-wrapper--year" bind:this={yearDropdownEl}>
    <button
      class="year-trigger"
      onclick={(e) => { e.stopPropagation(); yearDropdownOpen = !yearDropdownOpen; }}
    >
      {selectedYear} ▾
    </button>
    {#if yearDropdownOpen}
      <ul class="year-options">
        {#each years as year}
          <li>
            <button
              class:selected={String(year) === selectedYear}
              onclick={() => { selectedYear = String(year); yearDropdownOpen = false; document.dispatchEvent(new CustomEvent('ui:close')); }}
            >
              {year}
            </button>
          </li>
        {/each}
      </ul>
    {/if}
  </span>
  <span class="select-wrapper">
    <select bind:value={selectedOffice}>
      {#each offices as office}
        <option value={office}>{office}</option>
      {/each}
    </select>
  </span>
  <span class="select-wrapper">
    <select bind:value={selectedParty}>
      <option value="">--</option>
      {#each parties as party}
        <option value={party}>{party}</option>
      {/each}
    </select>
  </span>
</div>

<style lang="scss">
  @use "../../styles/variables.scss";

  .state-page__controls {
    display: flex;
    gap: variables.$spacing-xs;
    align-items: center;

    .select-wrapper {
      display: inline-block;
      position: relative;

      &:not(&--year)::after {
        content: '▾';
        position: absolute;
        right: 0.4rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 0.8rem;
        color: variables.$medium-gray;
        pointer-events: none;
      }

      select {
        appearance: none;
        background-color: variables.$white;
        border: 1px solid variables.$medium-gray;
        border-radius: variables.$border-radius;
        padding: 0 1.2rem 0 0.35rem;
        font-size: 0.85rem;
        font-weight: 400;
        color: variables.$dark-gray;
        cursor: pointer;

        &:focus {
          outline: none;
          border-color: variables.$royal-blue;
        }
      }

      &--year {
        position: relative;

        .year-trigger {
          background-color: variables.$white;
          border: 1px solid variables.$medium-gray;
          border-radius: variables.$border-radius;
          padding: 0 0.35rem;
          font-size: 0.85rem;
          font-weight: 400;
          color: variables.$dark-gray;
          cursor: pointer;

          &:focus {
            outline: none;
            border-color: variables.$royal-blue;
          }
        }

        .year-options {
          position: absolute;
          top: 100%;
          left: 0;
          z-index: 100;
          margin: 2px 0 0;
          padding: 0;
          list-style: none;
          background-color: variables.$white;
          border: 1px solid variables.$medium-gray;
          border-radius: variables.$border-radius;
          max-height: 16rem;
          overflow-y: auto;

          li button {
            display: block;
            width: 100%;
            padding: 2px 0.6rem;
            font-size: 0.85rem;
            font-weight: 400;
            color: variables.$dark-gray;
            background: none;
            border: none;
            cursor: pointer;
            text-align: left;
            white-space: nowrap;

            &:hover, &.selected {
              background-color: variables.$light-gray;
            }
          }
        }
      }
    }
  }

  @media (max-width: 768px) {
    .state-page__controls {
      width: 100%;
      flex-wrap: wrap;
    }
  }
</style>
