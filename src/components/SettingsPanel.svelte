<script lang="ts">
  import {
    valueNames,
    valueShortNames,
    popVarNames,
    popVarShortNames,
    scenarioNames,
    scenarioShortNames,
    validValues,
    validPopVars,
    getValidForYear,
  } from "../lib/manifest.js";
  import { chartState } from "../lib/chartState.svelte.js";
  import type { ValueType, PopVar, Scenario } from "../lib/values.js";

  let { showScenario = true }: { showScenario?: boolean } = $props();

  let panelOpen = $state(false);
  let valueOpen = $state(false);
  let popVarOpen = $state(false);
  let scenarioOpen = $state(false);
  let panelEl: HTMLDivElement | undefined;
  let valueSelectEl: HTMLDivElement | undefined;
  let popVarSelectEl: HTMLDivElement | undefined;
  let scenarioSelectEl: HTMLDivElement | undefined;

  function handlePanelPointerDown(e: PointerEvent) {
    if (valueOpen && !valueSelectEl?.contains(e.target as Node))
      valueOpen = false;
    if (popVarOpen && !popVarSelectEl?.contains(e.target as Node))
      popVarOpen = false;
    if (scenarioOpen && !scenarioSelectEl?.contains(e.target as Node))
      scenarioOpen = false;
  }

  const scenarios = Object.keys(scenarioShortNames) as Scenario[];

  // Full option lists (for display — always show all)
  const allValues = $derived(validValues[chartState.scenario]);
  const allPopVars = $derived(
    (validPopVars[chartState.value] ?? []) as PopVar[],
  );
  const showPopVar = $derived(allPopVars.length > 0);

  // Year-filtered subsets (used only to mark options disabled)
  const yearValid = $derived(
    getValidForYear(chartState.year, chartState.scenario),
  );
  const enabledValues = $derived(yearValid.values);
  const enabledPopVars = $derived(
    yearValid.popVarsFor(chartState.value) as PopVar[],
  );

  // Snap popVar if it becomes disabled when value or year changes
  $effect(() => {
    if (
      enabledPopVars.length > 0 &&
      !enabledPopVars.includes(chartState.popVar)
    ) {
      chartState.popVar = enabledPopVars[0];
    }
  });

  // Close panel on click outside
  $effect(() => {
    if (!panelOpen) return;
    const handler = (e: MouseEvent) => {
      if (!panelEl?.contains(e.target as Node)) {
        panelOpen = false;
        document.dispatchEvent(new CustomEvent("ui:close"));
      }
    };
    document.addEventListener("pointerdown", handler);
    return () => document.removeEventListener("pointerdown", handler);
  });

  function selectValue(v: ValueType) {
    chartState.value = v;
    valueOpen = false;
  }
  function selectPopVar(p: PopVar) {
    chartState.popVar = p;
    popVarOpen = false;
  }
</script>

<div class="settings" bind:this={panelEl}>
  <button
    class="settings__gear"
    class:active={panelOpen}
    onclick={() => (panelOpen = !panelOpen)}
    aria-label="Chart settings"
    aria-expanded={panelOpen}>⚙</button
  >

  {#if panelOpen}
    <div
      class="settings__panel"
      role="dialog"
      aria-label="Chart settings"
      onpointerdown={handlePanelPointerDown}
    >
      <!-- Value row -->
      <div class="row">
        <span class="row-label">
          <a href={`${import.meta.env.BASE_URL}about/definitions`} class="row-label__link"
            >Value-of-a-vote:</a
          >
        </span>
        <div
          class="custom-select"
          class:open={valueOpen}
          bind:this={valueSelectEl}
        >
          <button
            class="custom-select__trigger"
            onclick={() => {
              valueOpen = !valueOpen;
              popVarOpen = false;
            }}
            >{valueShortNames[chartState.value]}
            <span class="arrow">▾</span></button
          >
          {#if valueOpen}
            <div class="custom-select__list">
              {#each allValues as v}
                <button
                  class="custom-select__option"
                  class:selected={v === chartState.value}
                  disabled={!enabledValues.includes(v)}
                  onmousedown={() => selectValue(v)}>{valueNames[v]}</button
                >
              {/each}
            </div>
          {/if}
        </div>
      </div>

      <!-- PopVar row -->
      {#if showPopVar}
        <div class="row">
          <span class="row-label">
            <a href={`${import.meta.env.BASE_URL}about/population`} class="row-label__link"
              >Population Variable:</a
            >
          </span>
          <div
            class="custom-select"
            class:open={popVarOpen}
            bind:this={popVarSelectEl}
          >
            <button
              class="custom-select__trigger"
              onclick={() => {
                popVarOpen = !popVarOpen;
                valueOpen = false;
              }}
              >{popVarShortNames[chartState.popVar]}
              <span class="arrow">▾</span></button
            >
            {#if popVarOpen}
              <div class="custom-select__list">
                {#each allPopVars as p}
                  <button
                    class="custom-select__option"
                    class:selected={p === chartState.popVar}
                    disabled={!enabledPopVars.includes(p)}
                    onmousedown={() => selectPopVar(p)}>{popVarNames[p]}</button
                  >
                {/each}
              </div>
            {/if}
          </div>
        </div>
      {/if}

      <!-- Scenario row -->
      {#if showScenario}
      <div class="row">
        <span class="row-label">
          <a href={`${import.meta.env.BASE_URL}about/scenarios`} class="row-label__link"
            >Election Scenario:</a
          >
        </span>
        <div
          class="custom-select"
          class:open={scenarioOpen}
          bind:this={scenarioSelectEl}
        >
          <button
            class="custom-select__trigger"
            onclick={() => {
              scenarioOpen = !scenarioOpen;
              valueOpen = false;
              popVarOpen = false;
            }}
            >{scenarioShortNames[chartState.scenario]}
            <span class="arrow">▾</span></button
          >
          {#if scenarioOpen}
            <div class="custom-select__list">
              {#each scenarios as s}
                <button
                  class="custom-select__option"
                  class:selected={s === chartState.scenario}
                  onmousedown={() => {
                    chartState.scenario = s;
                    scenarioOpen = false;
                  }}>{scenarioNames[s]}</button
                >
              {/each}
            </div>
          {/if}
        </div>
      </div>
      {/if}
    </div>
  {/if}
</div>

<style lang="scss">
  @use "../styles/variables.scss";

  .settings {
    position: relative;
    display: inline-block;

    &__gear {
      background: none;
      border: none;
      font-size: 1.25rem;
      color: variables.$medium-gray;
      cursor: pointer;
      padding: 2px 5px;
      border-radius: 3px;
      line-height: 1;

      &:hover,
      &.active {
        color: variables.$dark-gray;
        background: variables.$light-gray;
      }
    }

    &__panel {
      position: absolute;
      top: calc(100% + 4px);
      right: 0;
      background: variables.$white;
      border: 1px solid #e0e0e0;
      border-radius: 6px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
      padding: 0.75rem 0.9rem;
      z-index: 200;
      min-width: 340px;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }
  }

  .row {
    display: grid;
    grid-template-columns: 1fr 8.4rem;
    align-items: center;
    gap: 0.15rem;
  }

  .row-label {
    font-size: 0.8rem;
    color: variables.$dark-gray;
    align-self: center;
  }

  .row-label__link {
    color: inherit;
    text-decoration: none;
    border-bottom: 1px dotted variables.$medium-gray;

    &:hover {
      color: variables.$dark-gray;
      border-bottom-color: variables.$dark-gray;
    }
  }

  /* custom select */
  .custom-select {
    position: relative;
    width: 8.4rem;

    &__trigger {
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: variables.$white;
      border: 1px solid #ccc;
      border-radius: 4px;
      padding: 3px 0.5rem;
      font-size: 0.8rem;
      color: variables.$dark-gray;
      cursor: pointer;
      text-align: left;

      &:focus {
        outline: none;
        border-color: variables.$royal-blue;
      }

      .arrow {
        font-size: 0.65rem;
        color: variables.$medium-gray;
        flex-shrink: 0;
      }
    }

    &__list {
      position: absolute;
      top: calc(100% + 2px);
      right: 0;
      width: max-content;
      min-width: 100%;
      background: variables.$white;
      border: 1px solid #ccc;
      border-radius: 4px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      z-index: 400;
      overflow: hidden;
    }

    &__option {
      display: block;
      width: 100%;
      text-align: left;
      background: none;
      border: none;
      padding: 5px 0.5rem;
      font-size: 0.8rem;
      color: variables.$dark-gray;
      cursor: pointer;
      white-space: nowrap;

      &:hover:not(:disabled) {
        background: variables.$light-gray;
      }

      &:disabled {
        color: #bfc2c6;
        cursor: not-allowed;
      }

      &.selected {
        font-weight: 600;
        color: variables.$royal-blue;
      }
    }
  }
</style>
