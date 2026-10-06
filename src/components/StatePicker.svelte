<script lang="ts">
  import { slide } from "svelte/transition";
  import Select from "./Select.svelte";
  import type { State, StatePO } from "../lib/states.js";

  type Props = {
    heading: string;
    states: State[];
    selectedState?: StatePO;
    selectedParty?: string;
    partyLabel?: string;
    forceShowParty?: boolean;
  };

  let {
    heading,
    states,
    selectedState = $bindable(""),
    selectedParty = $bindable(""),
    partyLabel = "Your party... (optional)",
    forceShowParty = false,
  }: Props = $props();
</script>

<div class="state-picker">
  <h3>{heading}</h3>
  <div class="form-group">
    <Select
      bind:value={selectedState}
      options={[
        { value: "", label: "-- select state --" },
        ...states.map((s) => ({ value: s.statePO, label: s.stateName })),
      ]}
      style="width: 100%"
    />
  </div>
  {#if selectedState || forceShowParty}
    <div class="form-group party-group" transition:slide={{ duration: 200 }}>
      <p class="party-label">{partyLabel}</p>
      <Select
        bind:value={selectedParty}
        options={[
          { value: "", label: "—" },
          { value: "democrat", label: "Democrat" },
          { value: "republican", label: "Republican" },
          { value: "other", label: "Other" },
        ]}
        style="width: 100%"
      />
    </div>
  {/if}
</div>

<style lang="scss">
  @use "../styles/variables.scss";

  .state-picker {
    h3 {
      font-size: variables.$font-size-medium;
      margin-bottom: variables.$spacing-sm;
      color: variables.$dark-gray;
    }

    .form-group {
      margin-bottom: variables.$spacing-sm;

      &:last-child {
        margin-bottom: 0;
      }

      .party-label {
        font-size: variables.$font-size-small;
        font-weight: 600;
        color: variables.$dark-gray;
        margin: 0 0 variables.$spacing-xs 0;
      }
    }
  }
</style>
