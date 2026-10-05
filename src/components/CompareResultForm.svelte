<script lang="ts">
  import { untrack } from "svelte";
  import { officesByName } from "../lib/elections";

  let {
    years,
    offices,
    states,
  }: {
    years: number[];
    offices: string[];
    states: { id: string; name: string }[];
  } = $props();

  const reverseOffices = Object.fromEntries(
    Object.entries(officesByName).map(([name, key]) => [key, name]),
  );

  const params =
    typeof window !== "undefined"
      ? new URLSearchParams(window.location.search)
      : new URLSearchParams();

  const electionParam = params.get("election") ?? "";
  const dashIdx = electionParam.indexOf("-");
  const yearPart = dashIdx >= 0 ? electionParam.slice(0, dashIdx) : "";
  const officePart = dashIdx >= 0 ? electionParam.slice(dashIdx + 1) : "";

  let myStatePO = $state(
    untrack(() => params.get("state1")?.toLowerCase() ?? ""),
  );
  let myParty = $state(untrack(() => params.get("party1") ?? ""));
  let cmpStatePO = $state(
    untrack(() => params.get("state2")?.toLowerCase() ?? ""),
  );
  let cmpParty = $state(untrack(() => params.get("party2") ?? ""));
  let selectedYear = $state(
    untrack(() => yearPart || String(years[0] ?? 2024)),
  );
  let selectedOffice = $state(
    untrack(() => reverseOffices[officePart] ?? offices[0] ?? ""),
  );

  const partiesOk = $derived(
    (myParty === "" && cmpParty === "") || (myParty !== "" && cmpParty !== ""),
  );
  const canGo = $derived(myStatePO !== "" && cmpStatePO !== "" && partiesOk);

  function navigate() {
    if (!canGo) return;
    const officeKey = officesByName[selectedOffice] ?? "president";
    let url = `${import.meta.env.BASE_URL}compare-result?state1=${myStatePO}&state2=${cmpStatePO}&election=${selectedYear}-${officeKey}`;
    if (myParty) url += `&party1=${myParty}`;
    if (cmpParty) url += `&party2=${cmpParty}`;
    window.location.href = url;
  }
</script>

<div class="compare-bar">
  <div class="compare-bar__group">
    <span class="compare-bar__label">you live in</span>
    <select bind:value={myStatePO}>
      <option value="">--</option>
      {#each states as state}
        <option value={state.id}>{state.name}</option>
      {/each}
    </select>
    <select bind:value={myParty}>
      <option value="">--</option>
      <option value="democrat">Democrat</option>
      <option value="republican">Republican</option>
      <option value="other">Other</option>
    </select>
  </div>

  <div class="compare-bar__group">
    <span class="compare-bar__label">comparing with</span>
    <select bind:value={cmpStatePO}>
      <option value="">--</option>
      {#each states as state}
        <option value={state.id}>{state.name}</option>
      {/each}
    </select>
    <select bind:value={cmpParty}>
      <option value="">--</option>
      <option value="democrat">Democrat</option>
      <option value="republican">Republican</option>
      <option value="other">Other</option>
    </select>
  </div>

  <button class="compare-bar__go" onclick={navigate} disabled={!canGo}
    >Go</button
  >
</div>

<div class="results-panel">
  <!-- results will go here -->
</div>

<style lang="scss">
  @use "../styles/variables.scss";

  .compare-bar {
    display: grid;
    grid-template-areas: "g1 g2 go";
    grid-template-columns: 1fr 1fr auto;
    align-items: center;
    gap: variables.$spacing-sm;
    padding: variables.$spacing-sm variables.$spacing-md;
    background: variables.$white;
    border: 1px solid #e5e7eb;
    border-radius: variables.$border-radius;
    margin-bottom: variables.$spacing-lg;

    @media (max-width: 600px) {
      grid-template-areas:
        "g1 go"
        "g2 go";
      grid-template-columns: 1fr auto;
    }

    &__group {
      display: flex;
      align-items: center;
      gap: variables.$spacing-xs;

      &:nth-child(1) {
        grid-area: g1;
        padding-right: variables.$spacing-sm;
        border-right: 1px solid #e5e7eb;

        @media (max-width: 600px) {
          padding-right: 0;
          padding-bottom: variables.$spacing-xs;
          border-right: none;
          border-bottom: 1px solid #e5e7eb;
        }
      }

      &:nth-child(2) {
        grid-area: g2;
      }
    }

    &__label {
      font-size: variables.$font-size-small;
      color: variables.$medium-gray;
      white-space: nowrap;
    }

    &__go {
      grid-area: go;
      align-self: stretch;
      background-color: variables.$dark-gray;
      color: variables.$white;
      border: none;
      border-radius: variables.$border-radius;
      padding: 4px variables.$spacing-sm;
      font-size: variables.$font-size-base;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
      transition: background-color variables.$transition-duration ease;

      &:hover:not(:disabled) {
        background-color: variables.$black;
      }

      &:disabled {
        opacity: 0.45;
        cursor: default;
      }
    }

    select {
      padding: 2px 4px;
      border: 1px solid variables.$medium-gray;
      border-radius: variables.$border-radius;
      font-size: variables.$font-size-small;
      background-color: variables.$white;
      color: variables.$dark-gray;
      cursor: pointer;
      min-width: 0;

      &:focus {
        outline: none;
        border-color: variables.$royal-blue;
      }
    }

    // State selects (first select in each group)
    &__group select:nth-child(2) {
      width: 120px;
    }

    // Party selects (second select in each group)
    &__group select:nth-child(3) {
      width: 100px;
    }
  }

  .results-panel {
    min-height: 300px;
  }
</style>
