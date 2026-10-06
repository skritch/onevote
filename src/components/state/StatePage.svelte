<script lang="ts">
  import {
    defaultStatePageParams,
    fromUrlParams,
    type StatePageParams,
  } from "../../lib/statePageParams.js";
  import { defaultValue, defaultPopVar } from "../../lib/manifest.js";
  import type { StatePO } from "../../lib/states.js";
  import type { DistrictData } from "../../lib/districts.js";
  import StateControls from "./StateControls.svelte";
  import SettingsPanel from "../SettingsPanel.svelte";
  import StateValueCard from "./StateValueCard.svelte";
  import StateFactBox from "./StateFactBox.svelte";
  import ElectionPlot from "../ElectionPlot.svelte";

  type Props = {
    years: number[];
    stateName: string;
    statePO: StatePO;
    districtData: DistrictData | null;
  };

  let { years, stateName, statePO, districtData }: Props = $props();

  const params = $state<StatePageParams>(
    typeof window !== "undefined"
      ? fromUrlParams(new URLSearchParams(window.location.search))
      : { ...defaultStatePageParams },
  );

  // Reveal page sections hidden by [data-state-loading] once state is applied.
  $effect(() => {
    document.documentElement.removeAttribute("data-state-loading");
  });

  // Write URL whenever any relevant state changes (skip first run).
  let urlSyncReady = false;
  // Once any non-default setting has appeared, always write all settings.
  let settingsWritten = false;
  $effect(() => {
    void [
      params.year,
      params.office,
      params.party,
      params.scenario,
      params.value,
      params.popVar,
      params.sort,
      params.district,
      params.districtId,
    ];
    if (!urlSyncReady) {
      urlSyncReady = true;
      return;
    }
    syncURL();
  });

  function syncURL() {
    const newUrl = new URL(window.location.href);

    if (
      params.year !== defaultStatePageParams.year ||
      params.office !== defaultStatePageParams.office
    ) {
      newUrl.searchParams.set("election", `${params.year}-${params.office}`);
    } else {
      newUrl.searchParams.delete("election");
    }

    if (params.party) newUrl.searchParams.set("party", params.party);
    else newUrl.searchParams.delete("party");

    if (params.scenario !== defaultStatePageParams.scenario)
      newUrl.searchParams.set("scenario", params.scenario);
    else newUrl.searchParams.delete("scenario");

    if (params.district) newUrl.searchParams.set("district", params.district);
    else newUrl.searchParams.delete("district");

    if (params.districtId)
      newUrl.searchParams.set("districtId", params.districtId);
    else newUrl.searchParams.delete("districtId");

    const defPop = defaultPopVar[params.value];
    const hasNonDefault =
      params.value !== defaultValue ||
      (defPop != null && params.popVar !== defPop) ||
      params.sort !== "alpha";
    if (hasNonDefault) settingsWritten = true;

    if (settingsWritten) {
      newUrl.searchParams.set("value", params.value);
      if (defPop != null) newUrl.searchParams.set("pop", params.popVar);
      else newUrl.searchParams.delete("pop");
      if (params.sort !== "alpha") newUrl.searchParams.set("sort", params.sort);
      else newUrl.searchParams.delete("sort");
    } else {
      newUrl.searchParams.delete("value");
      newUrl.searchParams.delete("pop");
      newUrl.searchParams.delete("sort");
    }

    window.history.replaceState({}, "", newUrl);
  }
</script>

<div class="state-page">
  <div class="page-header state-page__header">
    <h1>{stateName}</h1>
    <div class="page-controls">
      <StateControls {years} {statePO} {districtData} {params} />
      <SettingsPanel
        year={params.year}
        bind:value={params.value}
        bind:popVar={params.popVar}
        bind:scenario={params.scenario}
      />
    </div>
  </div>

  <div class="content-page">
    <div class="state-page__panels">
      <StateValueCard {stateName} {statePO} {params} />
      <StateFactBox {statePO} {districtData} {params} />
    </div>
    <div class="state-page__content">
      <ElectionPlot
        focusStatePO={statePO}
        scenario={params.scenario}
        year={params.office === "president" ? params.year : -1}
        value={params.value}
        popVar={params.popVar}
        bind:sort={params.sort}
      />
    </div>
  </div>
</div>

<style lang="scss">
  @use "../../styles/variables.scss";

  .state-page {
    h1 {
      font-size: variables.$font-size-large;
      color: variables.$dark-gray;
      margin: 0;
      white-space: nowrap;
    }

    &__header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: variables.$spacing-md;
      margin-bottom: variables.$spacing-md;
    }

    &__panels {
      display: grid;
      grid-template-columns: 55fr 45fr;
      gap: variables.$spacing-md;
      margin-bottom: variables.$spacing-md;
    }

    &__content {
      background-color: variables.$white;
      padding: variables.$spacing-md;
      border-radius: variables.$border-radius;
      border: 1px solid #e5e7eb;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.07);
    }

    @media (max-width: variables.$content-breakpoint) {
      &__header {
        flex-wrap: wrap;
      }

      &__panels {
        grid-template-columns: 1fr;
      }
    }
  }

  :global([data-state-loading] .page-controls),
  :global([data-state-loading] .state-page__panels),
  :global([data-state-loading] .state-page__content) {
    opacity: 0;
  }

  :global([data-state-loading] .state-logo) {
    opacity: 0;
  }
</style>
