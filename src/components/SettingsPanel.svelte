<script lang="ts">
  import {
    valueNames, valueShortNames,
    popVarNames, popVarShortNames,
    validPopVars, validValues,
  } from '../utils/manifest.js'
  import { chartState } from '../utils/chartState.svelte.js'
  import type { ValueType, PopVar } from '../utils/values.js'

  let panelOpen = $state(false)
  let valueOpen = $state(false)
  let popVarOpen = $state(false)
  let panelEl: HTMLDivElement | undefined

  const availableValues = $derived(validValues[chartState.scenario])
  const availablePopVars = $derived((validPopVars[chartState.value] ?? []) as PopVar[])
  const showPopVar = $derived(availablePopVars.length > 0)

  // Reset popVar if it becomes invalid when value changes
  $effect(() => {
    if (availablePopVars.length > 0 && !availablePopVars.includes(chartState.popVar)) {
      chartState.popVar = availablePopVars[0]
    }
  })

  // Close panel on click outside
  $effect(() => {
    if (!panelOpen) return
    const handler = (e: MouseEvent) => {
      if (!panelEl?.contains(e.target as Node)) panelOpen = false
    }
    document.addEventListener('pointerdown', handler)
    return () => document.removeEventListener('pointerdown', handler)
  })

  function selectValue(v: ValueType) { chartState.value = v; valueOpen = false }
  function selectPopVar(p: PopVar) { chartState.popVar = p; popVarOpen = false }
</script>

<div class="settings" bind:this={panelEl}>
  <button
    class="settings__gear"
    class:active={panelOpen}
    onclick={() => panelOpen = !panelOpen}
    aria-label="Chart settings"
    aria-expanded={panelOpen}
  >⚙</button>

  {#if panelOpen}
    <div class="settings__panel" role="dialog" aria-label="Chart settings">

      <!-- Value row -->
      <div class="row">
        <span class="row-label help">
          Value-of-a-vote Definition:
          <div class="help__tooltip" role="tooltip">
            Choose a definition of "value of a vote."
            See <a href="/about/definitions">here</a> for details.
          </div>
        </span>
        <div class="custom-select" class:open={valueOpen}>
          <button
            class="custom-select__trigger"
            onclick={() => { valueOpen = !valueOpen; popVarOpen = false }}
          >{valueShortNames[chartState.value]} <span class="arrow">▾</span></button>
          {#if valueOpen}
            <div class="custom-select__list">
              {#each availableValues as v}
                <button
                  class="custom-select__option"
                  class:selected={v === chartState.value}
                  onmousedown={() => selectValue(v)}
                >{valueNames[v]}</button>
              {/each}
            </div>
          {/if}
        </div>
      </div>

      <!-- PopVar row -->
      {#if showPopVar}
        <div class="row">
          <span class="row-label help">
            Population Definition:
            <div class="help__tooltip" role="tooltip">
              Choose which population measure to use.
              See <a href="/about/population">here</a> for details.
            </div>
          </span>
          <div class="custom-select" class:open={popVarOpen}>
            <button
              class="custom-select__trigger"
              onclick={() => { popVarOpen = !popVarOpen; valueOpen = false }}
            >{popVarShortNames[chartState.popVar]} <span class="arrow">▾</span></button>
            {#if popVarOpen}
              <div class="custom-select__list">
                {#each availablePopVars as p}
                  <button
                    class="custom-select__option"
                    class:selected={p === chartState.popVar}
                    onmousedown={() => selectPopVar(p)}
                  >{popVarNames[p]}</button>
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

      &:hover, &.active {
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
      box-shadow: 0 4px 16px rgba(0,0,0,0.12);
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
    grid-template-columns: 1fr 7rem;
    align-items: center;
    gap: 0.35rem;
  }

  .row-label {
    font-size: 0.8rem;
    color: variables.$dark-gray;
    cursor: help;
    border-bottom: 1px dotted variables.$medium-gray;
    align-self: center;
  }

  /* tooltip on the label */
  .help {
    position: relative;

    &__tooltip {
      display: none;
      position: absolute;
      bottom: calc(100% + 6px);
      left: 0;
      background: variables.$dark-gray;
      color: variables.$white;
      padding: 0.45rem 0.6rem;
      border-radius: 4px;
      font-size: 0.75rem;
      width: 210px;
      white-space: normal;
      z-index: 300;
      line-height: 1.4;
      pointer-events: none;

      a {
        color: #a8c4f0;
        pointer-events: auto;
      }

      &::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 0.6rem;
        border: 5px solid transparent;
        border-top-color: variables.$dark-gray;
      }
    }

    &:hover &__tooltip {
      display: block;
    }
  }

  /* custom select */
  .custom-select {
    position: relative;
    width: 7rem;

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
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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

      &:hover {
        background: variables.$light-gray;
      }

      &.selected {
        font-weight: 600;
        color: variables.$royal-blue;
      }
    }
  }
</style>
