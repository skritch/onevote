<script lang="ts">
  import { slide } from 'svelte/transition';
  import CustomSelect from './CustomSelect.svelte';

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
    <CustomSelect
      bind:value={selectedState}
      options={[{ value: '', label: '-- select state --' }, ...states.map(s => ({ value: s.id, label: s.name }))]}
      style="width: 100%"
    />
  </div>
  {#if selectedState || forceShowParty}
    <div class="form-group party-group" transition:slide={{ duration: 200 }}>
      <p class="party-label">{partyLabel}</p>
      <CustomSelect
        bind:value={selectedParty}
        options={[
          { value: '', label: '—' },
          { value: 'democrat', label: 'Democrat' },
          { value: 'republican', label: 'Republican' },
          { value: 'other', label: 'Other' },
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
