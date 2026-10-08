<script module lang="ts">
  import type { ValueType, PopVar, Scenario } from "../../lib/values.js";
  import type { Office } from "../../lib/elections.js";
  import type { Party } from "../../lib/party.js";
  import { displayScenarios } from "../../lib/manifest.js";

  export type SortMode = "value" | "alpha";

  export type StatePageParams = {
    scenario: Scenario;
    year: number;
    office: Office;
    value: ValueType;
    popVar: PopVar;
    sort: SortMode;
    party?: Party;
    district?: string;
    districtId?: string;
  };

  export const defaultStatePageParams: StatePageParams = {
    scenario: displayScenarios[0],
    year: 2024,
    office: "president" as Office,
    value: "av" as ValueType,
    popVar: "ap" as PopVar,
    sort: "alpha" as SortMode,
    party: undefined,
    district: undefined,
    districtId: undefined,
  };
</script>

<script lang="ts">
  import { readFromUrl, syncToUrl } from "../../utils/url.js";
  import type { StatePO } from "../../lib/states.js";
  import type { DistrictIndex } from "../../lib/districts.js";
  import StateControls from "./StateControls.svelte";
  import SettingsPanel from "../SettingsPanel.svelte";
  import StateValueCard from "../StateValueCard.svelte";
  import StateFactBox from "../StateFactBox.svelte";
  import ElectionPlot from "../ElectionPlot.svelte";

  type Props = {
    years: number[];
    stateName: string;
    statePO: StatePO;
    districtIndex: DistrictIndex | null;
  };

  let { years, stateName, statePO, districtIndex }: Props = $props();

  const params = $state<StatePageParams>(
    typeof window !== "undefined"
      ? readFromUrl(new URLSearchParams(window.location.search), defaultStatePageParams)
      : { ...defaultStatePageParams },
  );

  // Reveal page sections hidden by [data-state-loading] once state is applied.
  $effect(() => {
    document.documentElement.removeAttribute("data-state-loading");
  });

  // Write URL whenever any relevant state changes (skip first run).
  let urlSyncReady = false;
  $effect(() => {
    void [
      params.year, params.office, params.party, params.scenario,
      params.value, params.popVar, params.sort, params.district, params.districtId,
    ];
    if (!urlSyncReady) { urlSyncReady = true; return; }
    const newUrl = new URL(window.location.href);
    syncToUrl(params, defaultStatePageParams, newUrl);
    window.history.replaceState({}, "", newUrl);
  });
</script>

<div class="state-page">
  <div class="page-header state-page__header">
    <h1>{stateName}</h1>
    <div class="page-controls">
      <StateControls {years} {statePO} {districtIndex} {params} />
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
      <StateValueCard
        {stateName}
        {statePO}
        scenario={params.scenario}
        year={params.year}
        office={params.office}
        value={params.value}
        popVar={params.popVar}
        party={params.party}
        district={params.district}
        districtId={params.districtId}
      />
      <StateFactBox
        {statePO}
        {districtIndex}
        year={params.year}
        districtId={params.districtId}
        onDistrictChange={(id) => { params.districtId = id; }}
      />
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
