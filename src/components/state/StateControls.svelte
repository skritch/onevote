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

  let selectedYear = $state(untrack(() => {
    const now = new Date().getFullYear()
    return String(years.find(y => y <= now) ?? years[0] ?? 2024)
  }));
  let selectedOffice = $state(untrack(() => offices[0] ?? ""));
  let selectedParty = $state("");

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

  // Read URL params on mount (runs once — no reactive deps)
  $effect(() => {
    const params = new URLSearchParams(window.location.search);
    const election = params.get("election");
    if (election) {
      const [year, officeKey] = election.split("-");
      if (year) selectedYear = year;
      const displayName = Object.entries(officesByName).find(([, v]) => v === officeKey)?.[0];
      if (displayName) selectedOffice = displayName;
    }
    const party = params.get("party");
    if (party) {
      const matched = parties.find(p => p.toLowerCase() === party.toLowerCase());
      if (matched) selectedParty = matched;
    }
    const valueParam = params.get("value");
    if (valueParam && valueParam in valueNames) chartState.value = valueParam as ValueType;
    const popParam = params.get("pop");
    if (popParam && popParam in popVarNames) chartState.popVar = popParam as PopVar;
    const sortParam = params.get("sort");
    if (sortParam === 'alpha' || sortParam === 'value') chartState.sort = sortParam;
    const scenarioParam = params.get("scenario");
    if (scenarioParam === 'p1' || scenarioParam === 'p2' || scenarioParam === 'p5')
      chartState.scenario = scenarioParam as Scenario;
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
        padding: 1px 1.4rem 1px 0.4rem;
        font-size: 1.05rem;
        font-weight: 600;
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
          padding: 1px 0.4rem;
          font-size: 1.05rem;
          font-weight: 600;
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
            font-size: 1.05rem;
            font-weight: 600;
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
