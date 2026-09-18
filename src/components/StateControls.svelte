<script lang="ts">
  import { untrack } from 'svelte';
  import { officesByName } from '../utils/elections';

  let {
    years,
    offices,
  }: {
    years: number[];
    offices: string[];
  } = $props();

  let selectedYear = $state(untrack(() => String(years[0] ?? 2024)));
  let selectedOffice = $state(untrack(() => offices[0] ?? ''));

  $effect(() => {
    const params = new URLSearchParams(window.location.search);
    const election = params.get('election');
    if (election) {
      const [year, officeKey] = election.split('-');
      if (year) selectedYear = year;
      const displayName = Object.entries(officesByName).find(([, v]) => v === officeKey)?.[0];
      if (displayName) selectedOffice = displayName;
    }
  });

  function updateURL() {
    const officeKey = officesByName[selectedOffice] ?? 'president';
    const electionId = `${selectedYear}-${officeKey}`;
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.set('election', electionId);
    window.history.replaceState({}, '', newUrl);
  }
</script>

<div class="state-page__controls">
  <span class="select-wrapper">
    <select bind:value={selectedYear} onchange={updateURL}>
      {#each years as year}
        <option value={String(year)}>{year}</option>
      {/each}
    </select>
  </span>
  <span class="select-wrapper">
    <select bind:value={selectedOffice} onchange={updateURL}>
      {#each offices as office}
        <option value={office}>{office}</option>
      {/each}
    </select>
  </span>
</div>

<style lang="scss">
  @use "../styles/variables.scss";

  .state-page__controls {
    display: flex;
    gap: variables.$spacing-xs;
    align-items: center;

    .select-wrapper {
      display: inline-block;

      select {
        background-color: variables.$white;
        border: 2px solid variables.$medium-gray;
        border-radius: variables.$border-radius;
        padding: variables.$spacing-xs variables.$spacing-sm;
        font-size: variables.$font-size-medsmall;
        font-weight: 600;
        color: variables.$dark-gray;
        cursor: pointer;

        &:focus {
          outline: none;
          border-color: variables.$royal-blue;
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
