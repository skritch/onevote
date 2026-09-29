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

  let plotEl: HTMLDivElement | undefined
  let width = $state(600)

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

    const chart = horizontal
      ? Plot.plot({
          width,
          marginLeft: 36,
          x: { label: axisLabel, grid: true },
          y: { label: null, tickSize: 0 },
          marks: [
            Plot.barX(validRows, {
              y: 'state',
              x: 'value',
              sort: { y: '-x' },
              ...barOpts,
              tip: { ...barOpts.tip, format: { ...barOpts.tip.format, y: false, x: (v: number) => formatVal(v) } },
            }),
            Plot.ruleX([1], { stroke: '#999', strokeDasharray: '4 2' }),
          ],
        })
      : Plot.plot({
          width,
          marginBottom: 52,
          x: { label: null, tickRotate: -55, padding: 0.15 },
          y: { label: axisLabel, labelAnchor: 'center', labelArrow: 'none', grid: true },
          marks: [
            Plot.barY(validRows, {
              x: 'state',
              y: 'value',
              sort: { x: '-y' },
              ...barOpts,
            }),
            Plot.ruleY([1], { stroke: '#999', strokeDasharray: '4 2' }),
          ],
        })

    plotEl.innerHTML = ''
    plotEl.appendChild(chart)
  })
</script>

<div class="plot-wrap" bind:clientWidth={width}>
  <div bind:this={plotEl}></div>
</div>

<style lang="scss">
  .plot-wrap {
    width: 100%;
    min-height: 180px;

    :global(svg) {
      display: block;
    }

    :global(.no-data) {
      color: #6c757d;
      text-align: center;
      padding: 2rem 0;
      font-size: 0.9rem;
    }
  }
</style>
