<script lang="ts">
  import { untrack } from "svelte";
  import { fly, fade } from "svelte/transition";
  import { officesByName } from "../utils/elections";
  import StatePicker from "./StatePicker.svelte";

  let {
    years,
    offices,
    states,
    initialCompareMode = false,
    initialShowParty = false,
  }: {
    years: number[];
    offices: string[];
    states: { id: string; name: string }[];
    initialCompareMode?: boolean;
    initialShowParty?: boolean;
  } = $props();

  let selectedYear = $state(untrack(() => String(years[0] ?? 2024)));
  let selectedOffice = $state(untrack(() => offices[0] ?? ""));
  let myState = $state("");
  let myParty = $state("");
  let compareState = $state("");
  let compareParty = $state("");
  let compareMode = $state(untrack(() => initialCompareMode));
  let showParty = $state(untrack(() => initialShowParty));

  $effect(() => {
    if (myState !== "" || compareState !== "") showParty = true;
  });

  // When user picks a party, default the other side to the opposite
  $effect(() => {
    if (myParty === "democrat") compareParty = "republican";
    else if (myParty === "republican") compareParty = "democrat";
  });

  function navigate() {
    if (!myState) return;
    const officeKey = officesByName[selectedOffice] ?? "president";
    let url = `/states/${myState}?election=${selectedYear}-${officeKey}`;
    if (myParty) url += `&party=${myParty}`;
    window.location.href = url;
  }

  function navigateCompare() {
    if (!myState || !compareState) return;
    const officeKey = officesByName[selectedOffice] ?? "president";
    let url = `/compare-result?state1=${myState}&state2=${compareState}&election=${selectedYear}-${officeKey}`;
    if (myParty) url += `&party1=${myParty}`;
    if (compareParty) url += `&party2=${compareParty}`;
    window.location.href = url;
  }

  const partiesOk = $derived(
    (myParty === "" && compareParty === "") ||
      (myParty !== "" && compareParty !== ""),
  );
  const canGo = $derived(
    compareMode
      ? myState !== "" && compareState !== "" && partiesOk
      : myState !== "",
  );
</script>

<div class="main-content__question">
  How much will your vote be worth in the
  <span class="select-wrapper">
    <select bind:value={selectedYear}>
      {#each years as year}
        <option value={String(year)}>{year}</option>
      {/each}
    </select>
  </span>
  <span class="select-wrapper">
    <select bind:value={selectedOffice}>
      {#each offices as office}
        <option value={office}>{office}</option>
      {/each}
    </select>
  </span>
  election?
</div>

<div class="pickers-wrapper" class:compare-mode={compareMode}>
  <div class="pickers-row" class:compare-mode={compareMode}>
    <div class="picker-card">
      <StatePicker
        heading="You live in..."
        {states}
        bind:selectedState={myState}
        bind:selectedParty={myParty}
        forceShowParty={showParty}
      />
    </div>
    {#if compareMode}
      <div
        class="picker-card"
        in:fly={{ x: 60, duration: 250 }}
        out:fade={{ duration: 150 }}
      >
        <button
          class="close-compare"
          onclick={() => (compareMode = false)}
          aria-label="Close comparison">×</button
        >
        <StatePicker
          heading="Compare with..."
          {states}
          bind:selectedState={compareState}
          bind:selectedParty={compareParty}
          partyLabel="Their party... (optional)"
          forceShowParty={showParty}
        />
      </div>
    {/if}
  </div>

  <button
    class="go-button"
    onclick={compareMode ? navigateCompare : navigate}
    disabled={!canGo}
  >
    Go
  </button>

  {#if !compareMode}
    <button class="compare-link" onclick={() => (compareMode = true)}>
      or, compare with another state →
    </button>
  {/if}
</div>

<style lang="scss">
  @use "../styles/variables.scss";

  .main-content__question {
    text-align: center;
    font-size: variables.$font-size-medium;
    font-weight: 600;
    color: variables.$dark-gray;
    line-height: 1.4;
    padding: variables.$spacing-lg 0 variables.$spacing-xl 0;

    @media (min-width: 769px) {
      white-space: nowrap;
      width: 100vw;
      position: relative;
      left: 50%;
      right: 50%;
      margin-left: -50vw;
      margin-right: -50vw;
    }

    .select-wrapper {
      display: inline-block;
      position: relative;

      select {
        background-color: variables.$white;
        border: 2px solid variables.$medium-gray;
        border-radius: variables.$border-radius;
        padding: 2px variables.$spacing-xs;
        font-size: variables.$font-size-medsmall;
        font-weight: 600;
        color: variables.$dark-gray;
        cursor: pointer;
      }
    }
  }

  @media (max-width: 768px) {
    .main-content__question {
      font-size: 1.25rem;
    }
  }

  .pickers-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: variables.$spacing-sm;
    margin-bottom: variables.$spacing-xl;
  }

  .pickers-row {
    display: flex;
    justify-content: center;
    gap: variables.$spacing-md;
    max-width: 360px;
    width: 100%;
    transition: max-width 0.25s ease;

    &.compare-mode {
      max-width: 752px;
    }
  }

  .picker-card {
    flex: 0 0 360px;
    width: 360px;
    min-width: 0;
    padding: variables.$spacing-md;
    background-color: variables.$white;
    border-radius: variables.$border-radius;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid #e5e7eb;
    position: relative;
  }

  .close-compare {
    position: absolute;
    top: variables.$spacing-xs;
    right: variables.$spacing-xs;
    background: none;
    border: none;
    color: variables.$medium-gray;
    font-size: 1.25rem;
    line-height: 1;
    cursor: pointer;
    padding: 2px 6px;
    border-radius: variables.$border-radius;

    &:hover {
      color: variables.$dark-gray;
      background-color: variables.$light-gray;
    }
  }

  .go-button {
    width: 100%;
    max-width: 360px;
    background-color: variables.$dark-gray;
    color: variables.$white;
    border: none;
    border-radius: variables.$border-radius;
    padding: variables.$spacing-xs variables.$spacing-md;
    font-size: variables.$font-size-base;
    font-weight: 600;
    cursor: pointer;
    transition: background-color variables.$transition-duration ease;

    &:hover:not(:disabled) {
      background-color: variables.$black;
    }

    &:disabled {
      opacity: 0.45;
      cursor: default;
    }
  }

  .compare-link {
    background: none;
    border: none;
    font-size: variables.$font-size-base;
    color: variables.$medium-gray;
    cursor: pointer;
    padding: 0;
    text-decoration: none;

    &:hover {
      color: variables.$dark-gray;
    }
  }

  @media (max-width: 768px) {
    .pickers-row {
      flex-direction: column;
      max-width: 360px;

      &.compare-mode {
        max-width: 360px;
      }
    }

    .go-button {
      max-width: 360px;
    }
  }
</style>
