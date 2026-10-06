<script lang="ts">
  import ElectionPlot from "./ElectionPlot.svelte";
  import { statePageParams } from "../lib/statePageParams.svelte.js";
  import { validPopVars } from "../lib/manifest.js";

  let { focusStatePO }: { focusStatePO: string } = $props();

  const showPopVar = $derived(
    (validPopVars[statePageParams.value] ?? []).length > 0,
  );
</script>

<ElectionPlot
  {focusStatePO}
  scenario={statePageParams.scenario}
  year={statePageParams.office === "president" ? statePageParams.year : -1}
  value={statePageParams.value}
  popVar={showPopVar ? statePageParams.popVar : undefined}
/>
