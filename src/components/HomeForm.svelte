<script lang="ts">
  import { untrack } from 'svelte';
  import { officesByName } from '../utils/elections';

  let {
    years,
    offices,
    states,
  }: {
    years: number[];
    offices: string[];
    states: { id: string; name: string }[];
  } = $props();

  let selectedYear = $state(untrack(() => String(years[0] ?? 2024)));
  let selectedOffice = $state(untrack(() => offices[0] ?? ''));
  let selectedState = $state('');

  function navigate() {
    if (!selectedState) return;
    const officeKey = officesByName[selectedOffice] ?? 'president';
    window.location.href = `/states/${selectedState}?election=${selectedYear}-${officeKey}`;
  }
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

<div class="comparison-container">
  <div class="comparison-container__side">
    <h3>You live in...</h3>
    <div class="form-group">
      <select bind:value={selectedState}>
        <option value="">--select state--</option>
        {#each states as state}
          <option value={state.id}>{state.name}</option>
        {/each}
      </select>
    </div>
    <button class="comparison-container__button" onclick={navigate}>Go</button>
  </div>
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

  .comparison-container {
    display: flex;
    align-items: stretch;
    justify-content: center;
    gap: variables.$spacing-md;
    max-width: 440px;
    margin: 0 auto variables.$spacing-xl auto;
    position: relative;

    &__side {
      flex: 1;
      padding: variables.$spacing-lg;
      background-color: variables.$white;
      border-radius: variables.$border-radius;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      border: 1px solid #e5e7eb;
      text-align: center;

      h3 {
        font-size: variables.$font-size-medium;
        margin-bottom: variables.$spacing-md;
        color: variables.$dark-gray;
      }

      .form-group {
        margin-bottom: variables.$spacing-md;
        text-align: left;

        select {
          width: 100%;
          padding: variables.$spacing-xs variables.$spacing-sm;
          border: 1px solid variables.$medium-gray;
          border-radius: variables.$border-radius;
          font-size: variables.$font-size-base;
          background-color: variables.$white;

          &:focus {
            outline: none;
            border-color: variables.$royal-blue;
          }
        }
      }
    }

    &__button {
      width: 100%;
      background-color: variables.$dark-gray;
      color: variables.$white;
      border: none;
      border-radius: variables.$border-radius;
      padding: variables.$spacing-xs variables.$spacing-md;
      font-size: variables.$font-size-base;
      font-weight: 600;
      cursor: pointer;
      transition: all variables.$transition-duration ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: variables.$spacing-xs;

      &:hover {
        background-color: variables.$black;
      }

      &::after {
        content: "→";
      }
    }

    @media (max-width: 768px) {
      flex-direction: column;
      gap: variables.$spacing-sm;

      &__button {
        position: relative;
        transform: none;
        margin: variables.$spacing-sm 0;

        &:hover {
          transform: scale(1.05);
        }
      }

      &__side {
        width: 100%;
      }
    }
  }
</style>
