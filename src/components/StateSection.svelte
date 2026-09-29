<script lang="ts">
  import StateValuePlot from './StateValuePlot.svelte'
  import { chartState } from '../utils/chartState.svelte.js'
  import { validPopVars } from '../utils/manifest.js'

  let { focusState }: { focusState: string } = $props()

  const showPopVar = $derived((validPopVars[chartState.value] ?? []).length > 0)
</script>

<StateValuePlot
  {focusState}
  scenario={chartState.scenario}
  year={chartState.year}
  value={chartState.value}
  popVar={showPopVar ? chartState.popVar : undefined}
/>
