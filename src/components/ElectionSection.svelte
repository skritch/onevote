<script lang="ts">
  import ElectionPlot from "./ElectionPlot.svelte";
  import { chartState } from "../lib/chartState.svelte.js";
  import { validPopVars } from "../lib/manifest.js";

  let { focusStatePO }: { focusStatePO: string } = $props();

  const showPopVar = $derived(
    (validPopVars[chartState.value] ?? []).length > 0,
  );
</script>

<ElectionPlot
  {focusStatePO}
  scenario={chartState.scenario}
  year={chartState.office === "president" ? chartState.year : -1}
  value={chartState.value}
  popVar={showPopVar ? chartState.popVar : undefined}
/>
