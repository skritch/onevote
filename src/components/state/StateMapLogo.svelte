<script lang="ts">
  import { chartState } from "../../lib/chartState.svelte.js";

  type DistrictData = {
    year_to_congress: Record<string, number>;
    districts_by_congress: Record<string, Record<string, string>>;
    viewbox_by_congress?: Record<string, string>;
  };

  let { districtData }: { districtData: DistrictData } = $props();

  const congress = $derived(districtData.year_to_congress[chartState.year]);

  const paths = $derived(
    congress == null ? [] : Object.values(districtData.districts_by_congress[congress] ?? {})
  );

  const viewBox = $derived(
    (congress != null && districtData.viewbox_by_congress?.[congress])
      ? districtData.viewbox_by_congress[congress]
      : "14 14 772 572"
  );
</script>

{#if paths.length > 0}
  <svg
    class="state-logo"
    viewBox={viewBox}
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <g class="state-logo__districts">
      {#each paths as d}
        <path {d} />
      {/each}
    </g>
  </svg>
{/if}

<style lang="scss">
  @use "../../styles/variables.scss";

  .state-logo {
    display: block;
    width: auto;
    height: auto;
    max-width: 100%;
    max-height: 14rem;

    &__districts path {
      fill: variables.$light-gray;
      stroke: #5a6a7a;
      stroke-width: 1px;
      vector-effect: non-scaling-stroke;
    }
  }
</style>
