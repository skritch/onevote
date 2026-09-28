<script lang="ts">
  import { slide } from 'svelte/transition';

  let {
    heading,
    states,
    selectedState = $bindable(''),
    selectedParty = $bindable(''),
    partyLabel = 'Your party... (optional)',
    forceShowParty = false,
  }: {
    heading: string;
    states: { id: string; name: string }[];
    selectedState?: string;
    selectedParty?: string;
    partyLabel?: string;
    forceShowParty?: boolean;
  } = $props();
</script>

<div class="state-picker">
  <h3>{heading}</h3>
  <div class="form-group">
    <select bind:value={selectedState}>
      <option value="">--select state--</option>
      {#each states as state}
        <option value={state.id}>{state.name}</option>
      {/each}
    </select>
  </div>
  {#if selectedState || forceShowParty}
    <div class="form-group party-group" transition:slide={{ duration: 200 }}>
      <p class="party-label">{partyLabel}</p>
      <select bind:value={selectedParty}>
        <option value="">--</option>
        <option value="democrat">Democrat</option>
        <option value="republican">Republican</option>
        <option value="other">Other</option>
      </select>
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

      select {
        width: 100%;
        padding: variables.$spacing-xs variables.$spacing-sm;
        border: 1px solid variables.$medium-gray;
        border-radius: variables.$border-radius;
        font-size: variables.$font-size-base;
        background-color: variables.$white;
        cursor: pointer;

        &:focus {
          outline: none;
          border-color: variables.$royal-blue;
        }
      }
    }
  }
</style>
