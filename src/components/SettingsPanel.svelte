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
  import CustomSelect from "./CustomSelect.svelte";

  let { showScenario = true }: { showScenario?: boolean } = $props();

  let panelOpen = $state(false);
  let panelEl: HTMLDivElement | undefined;

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

  const valueOptions = $derived(
    allValues.map((v) => ({
      value: v,
      label: valueNames[v],
      disabled: !enabledValues.includes(v),
    })),
  );
  const popVarOptions = $derived(
    allPopVars.map((p) => ({
      value: p,
      label: popVarNames[p],
      disabled: !enabledPopVars.includes(p),
    })),
  );
  const scenarioOptions = $derived(
    scenarios.map((s) => ({ value: s, label: scenarioNames[s] })),
  );

  // Local string mirrors for bind compatibility
  let valueVal = $state(chartState.value as string);
  let popVarVal = $state(chartState.popVar as string);
  let scenarioVal = $state(chartState.scenario as string);
  $effect(() => {
    chartState.value = valueVal as ValueType;
  });
  $effect(() => {
    chartState.popVar = popVarVal as PopVar;
  });
  $effect(() => {
    chartState.scenario = scenarioVal as Scenario;
  });
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
    <div class="settings__panel" role="dialog" aria-label="Chart settings">
      <!-- Value row -->
      <div class="row">
        <span class="row-label">
          <a
            href={`${import.meta.env.BASE_URL}about/definitions/`}
            class="row-label__link">Value-of-a-vote:</a
          >
        </span>
        <CustomSelect
          bind:value={valueVal}
          options={valueOptions}
          triggerLabel={valueShortNames[
            valueVal as keyof typeof valueShortNames
          ]}
          style="width: 100%"
        />
      </div>

      <!-- PopVar row -->
      {#if showPopVar}
        <div class="row">
          <span class="row-label">
            <a
              href={`${import.meta.env.BASE_URL}about/population/`}
              class="row-label__link">Population Variable:</a
            >
          </span>
          <CustomSelect
            bind:value={popVarVal}
            options={popVarOptions}
            triggerLabel={popVarShortNames[
              popVarVal as keyof typeof popVarShortNames
            ]}
            style="width: 100%"
          />
        </div>
      {/if}

      <!-- Scenario row -->
      {#if showScenario}
        <div class="row">
          <span class="row-label">
            <a
              href={`${import.meta.env.BASE_URL}about/scenarios/`}
              class="row-label__link">Election Scenario:</a
            >
          </span>
          <CustomSelect
            bind:value={scenarioVal}
            options={scenarioOptions}
            triggerLabel={scenarioShortNames[
              scenarioVal as keyof typeof scenarioShortNames
            ]}
            style="width: 100%"
          />
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
</style>
