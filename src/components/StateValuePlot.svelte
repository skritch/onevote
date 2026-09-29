<script lang="ts">
  import * as Plot from '@observablehq/plot'
  import { getPlotRows, partyColors } from '../utils/values.js'
  import type { Scenario, ValueType, PopVar } from '../utils/values.js'
  import { valueNames } from '../utils/manifest.js'
  import statesRaw from '../data/states.json'

  const stateNames: Record<string, string> = Object.fromEntries(
    (statesRaw as Array<{ id: string; name: string }>).map(s => [s.id.toUpperCase(), s.name])
  )

  let {
    scenario = 'p2' as Scenario,
    year = 2024,
    focusState,
    value = 'av' as ValueType,
    popVar = undefined as PopVar | undefined,
  }: {
    scenario?: Scenario
    year?: number
    focusState: string  // lowercase stateId from page params
    value?: ValueType
    popVar?: PopVar
  } = $props()

  type SortMode = 'value' | 'alpha'
  let sortMode = $state<SortMode>('value')

  let plotEl: HTMLDivElement | undefined
  let optionsEl: HTMLDivElement | undefined
  let width = $state(600)
  let optionsOpen = $state(false)

  $effect(() => {
    if (!optionsOpen) return
    const handler = (e: MouseEvent) => {
      if (!optionsEl?.contains(e.target as Node)) optionsOpen = false
    }
    document.addEventListener('pointerdown', handler)
    return () => document.removeEventListener('pointerdown', handler)
  })

  $effect(() => {
    if (!plotEl) return

    const stateCode = focusState.toUpperCase()
    const rows = getPlotRows(scenario, year, stateCode, value, popVar)
    const validRows = rows.filter(r => r.value !== null)

    if (validRows.length === 0) {
      plotEl.innerHTML = '<p class="no-data">No data available for this combination.</p>'
      return
    }

    const horizontal = width < 520
    const fill = (d: (typeof rows)[0]) => partyColors[d.winningParty ?? 'unknown']
    const fillOpacity = (d: (typeof rows)[0]) => (d.isFocus ? 1 : 0.38)
    const stateName = (d: (typeof rows)[0]) => stateNames[d.state] ?? d.state
    const formatVal = (v: number) => v.toFixed(3)

    const barOpts = {
      fill,
      fillOpacity,
      channels: { State: { value: stateName, label: 'State' } },
      tip: { format: { State: true, x: false, y: (v: number) => formatVal(v), fill: false, fillOpacity: false } },
    }

    const axisLabel = valueNames[value]
    const fontStyle = "font-family: Inter, Roboto, 'Helvetica Neue', Arial, sans-serif;"

    const xSort = sortMode === 'value' ? { x: '-y' } : { x: 'x' }
    const ySort = sortMode === 'value' ? { y: '-x' } : { y: 'y' }

    const chart = horizontal
      ? Plot.plot({
          width,
          height: 600,
          marginLeft: 36,
          style: fontStyle,
          x: { label: axisLabel, grid: true },
          y: { label: null },
          marks: [
            Plot.axisY({ fontSize: 8, tickSize: 0 }),
            Plot.barX(validRows, {
              y: 'state',
              x: 'value',
              sort: ySort,
              ...barOpts,
              tip: { ...barOpts.tip, format: { ...barOpts.tip.format, y: false, x: (v: number) => formatVal(v) } },
            }),
            Plot.ruleX([1], { stroke: '#999', strokeDasharray: '4 2' }),
          ],
        })
      : Plot.plot({
          width,
          height: 300,
          marginBottom: 52,
          style: fontStyle,
          x: { label: null, padding: 0.15 },
          y: { label: axisLabel, labelAnchor: 'center', labelArrow: 'none', grid: true },
          marks: [
            Plot.axisX({ tickRotate: -55, fontSize: 9 }),
            Plot.barY(validRows, {
              x: 'state',
              y: 'value',
              sort: xSort,
              ...barOpts,
            }),
            Plot.ruleY([1], { stroke: '#999', strokeDasharray: '4 2' }),
          ],
        })

    plotEl.innerHTML = ''
    plotEl.appendChild(chart)
  })
</script>

<div class="plot-outer">
  <div class="plot-content">
    <div bind:this={plotEl} bind:clientWidth={width}></div>
  </div>
  <div class="plot-toolbar">
    <div class="toolbar-item" bind:this={optionsEl}>
      <button
        class="toolbar-item__btn"
        class:active={optionsOpen}
        onclick={() => optionsOpen = !optionsOpen}
        aria-label="Sort options"
        aria-expanded={optionsOpen}
      >⇅</button>
      {#if optionsOpen}
        <div class="toolbar-item__panel" role="dialog" aria-label="Sort options">
          <button
            class="toolbar-item__choice"
            class:selected={sortMode === 'value'}
            onmousedown={() => { sortMode = 'value'; optionsOpen = false }}
          >by value</button>
          <button
            class="toolbar-item__choice"
            class:selected={sortMode === 'alpha'}
            onmousedown={() => { sortMode = 'alpha'; optionsOpen = false }}
          >A–Z</button>
        </div>
      {/if}
    </div>
  </div>
</div>

<style lang="scss">
  @use "../styles/variables.scss";

  $border-color: #d0d0d0;
  $btn-size: 26px;

  .plot-outer {
    display: flex;
    align-items: flex-start;
    width: 100%;
  }

  .plot-content {
    flex: 1;
    min-width: 0;
    border: 0.5px solid $border-color;
    border-radius: 4px;
    min-height: 180px;
    padding: 0 12px;

    :global(svg) {
      display: block;
    }

    :global(.no-data) {
      color: variables.$medium-gray;
      text-align: center;
      padding: 2rem 0;
      font-size: 0.9rem;
    }
  }

  .plot-toolbar {
    display: flex;
    flex-direction: column;
    margin-left: 4px;
    gap: 2px;
  }

  .toolbar-item {
    position: relative;

    &__btn {
      width: $btn-size;
      height: $btn-size;
      display: flex;
      align-items: center;
      justify-content: center;
      background: none;
      border: none;
      border-radius: 3px;
      font-size: 0.7rem;
      color: variables.$medium-gray;
      cursor: pointer;
      padding: 0;

      &:hover, &.active {
        background: variables.$light-gray;
        color: variables.$dark-gray;
      }
    }

    &__panel {
      position: absolute;
      top: calc(100% + 4px);
      right: 0;
      background: variables.$white;
      border: 1px solid $border-color;
      border-radius: 4px;
      box-shadow: 0 3px 12px rgba(0, 0, 0, 0.1);
      padding: 0.3rem 0.4rem;
      z-index: 200;
      display: flex;
      flex-direction: column;
      gap: 1px;
      white-space: nowrap;
    }

    &__choice {
      font-size: 0.68rem;
      padding: 3px 8px;
      border: none;
      border-radius: 3px;
      background: none;
      color: variables.$medium-gray;
      cursor: pointer;
      text-align: left;

      &:hover {
        background: variables.$light-gray;
        color: variables.$dark-gray;
      }

      &.selected {
        color: variables.$royal-blue;
        font-weight: 600;
      }
    }
  }
</style>
