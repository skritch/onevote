<script lang="ts">
  import { untrack } from "svelte";
  import {
    officesByName,
    dimensionsStateWinner,
    getDistrictDimension,
  } from "../../lib/elections";
  import type { StatePO } from "../../lib/states.js";
  import { statePageParams } from "../../lib/statePageParams.svelte.js";
  import {
    valueNames,
    popVarNames,
    defaultValue,
    defaultPopVar,
    getValidForYear,
  } from "../../lib/manifest.js";
  import { getDistrictsForState } from "../../lib/values.js";
  import type { ValueType, PopVar, Scenario } from "../../lib/values.js";
  import { getAvailableDistrictIds } from "../../lib/districts.js";
  import type { DistrictData } from "../../lib/districts.js";
  import Select from "../Select.svelte";
  import { PARTIES, type Party } from "../../lib/party.js";

  type Props = {
    years: number[];
    offices: string[];
    statePO?: StatePO;
    districtData?: DistrictData | null;
  };

  let { years, offices, statePO = "", districtData = null }: Props = $props();

  const _urlParams =
    typeof window !== "undefined"
      ? new URLSearchParams(window.location.search)
      : null;
  const _election = _urlParams?.get("election") ?? null;
  const [_yearParam, _officeParam] = _election
    ? _election.split("-")
    : [null, null];

  // Apply statePageParams fields from URL before effects run
  if (_urlParams) {
    const scenarioParam = _urlParams.get("scenario");
    if (
      scenarioParam === "p1" ||
      scenarioParam === "p2" ||
      scenarioParam === "p3" ||
      scenarioParam === "p4" ||
      scenarioParam === "p5"
    )
      statePageParams.scenario = scenarioParam as Scenario;
    const valueParam = _urlParams.get("value");
    if (valueParam && valueParam in valueNames)
      statePageParams.value = valueParam as ValueType;
    const popParam = _urlParams.get("pop");
    if (popParam && popParam in popVarNames)
      statePageParams.popVar = popParam as PopVar;
    const sortParam = _urlParams.get("sort");
    if (sortParam === "alpha" || sortParam === "value")
      statePageParams.sort = sortParam;
    const districtParam = _urlParams.get("district");
    if (districtParam) statePageParams.district = districtParam;
    const districtIdParam = _urlParams.get("districtId");
    if (districtIdParam) statePageParams.districtId = districtIdParam;
  }

  const _initialYear = (() => {
    if (_yearParam && years.includes(Number(_yearParam))) return _yearParam;
    const now = new Date().getFullYear();
    return String(years.find((y) => y <= now) ?? years[0] ?? 2024);
  })();
  const _initialOffice = (() => {
    if (_officeParam) {
      const displayName = Object.entries(officesByName).find(
        ([, v]) => v === _officeParam,
      )?.[0];
      if (displayName) return displayName;
    }
    return offices[0] ?? "";
  })();
  const _partyParam = _urlParams?.get("party") ?? null;

  let selectedYear = $state(_initialYear);
  let selectedOffice = $state(_initialOffice);
  let selectedParty = $state(
    (_partyParam
      ? (PARTIES.find((p) => p.toLowerCase() === _partyParam.toLowerCase()) ??
        undefined)
      : "undefined") as Party | undefined,
  );

  // Sync local selectors → statePageParams
  $effect(() => {
    statePageParams.year = Number(selectedYear);
  });
  $effect(() => {
    statePageParams.office = officesByName[selectedOffice] ?? "president";
  });
  $effect(() => {
    statePageParams.party = selectedParty;
  });

  // Auto-select winning party when WVV is chosen
  $effect(() => {
    if (statePageParams.value !== "wvv") return;
    untrack(() => {
      const year = statePageParams.year;
      const districtId = statePageParams.districtId;
      const scenario = statePageParams.scenario;
      let winner: string | null = null;
      if (scenario === "p3" && districtId) {
        winner =
          getDistrictDimension(year, statePO, districtId)?.winningParty ?? null;
      }
      if (!winner) {
        winner = dimensionsStateWinner[String(year)]?.[statePO] ?? null;
      }
      if (winner) {
        const winningParty =
          PARTIES.find((p) => p.toLowerCase() === winner.toLowerCase()) ??
          undefined;
        selectedParty = winningParty;
      }
    });
  });

  // Congressional districts for this state page, keyed by year
  const availableDistrictIds = $derived(
    districtData
      ? getAvailableDistrictIds(districtData, Number(selectedYear))
      : [],
  );

  const showDistrictIdSelector = true;
  const districtIdSelectorDisabled = $derived(
    availableDistrictIds.length === 0 ||
      (availableDistrictIds.length === 1 && availableDistrictIds[0] === "AL") ||
      Number(selectedYear) < 2012,
  );

  // Reset districtId when it becomes invalid (year change, at-large, etc.)
  $effect(() => {
    const year = Number(selectedYear);
    const available = availableDistrictIds;
    const isAtLarge = available.length === 1 && available[0] === "AL";
    const curDistrict = untrack(() => statePageParams.districtId);
    if (!curDistrict) return;
    if (
      year < 2012 ||
      available.length === 0 ||
      isAtLarge ||
      !available.includes(curDistrict)
    ) {
      statePageParams.districtId = "";
    }
  });

  // Available districts for this state under the current scenario/year
  const availableDistricts = $derived(
    statePO
      ? getDistrictsForState(
          statePageParams.scenario,
          statePageParams.year,
          statePO,
        )
      : [],
  );

  // Reset district when scenario doesn't support districts or district is no longer valid
  $effect(() => {
    const scenario = statePageParams.scenario;
    const available = availableDistricts;
    if (scenario !== "p3" && scenario !== "p4") {
      if (untrack(() => statePageParams.district))
        statePageParams.district = "";
    } else if (
      statePageParams.district &&
      !available.includes(statePageParams.district)
    ) {
      statePageParams.district = "";
    }
  });

  // Snap value/popVar to a valid combo when year or scenario changes
  $effect(() => {
    const year = Number(selectedYear);
    const { values, popVarsFor } = getValidForYear(
      year,
      statePageParams.scenario,
    );
    const curVal = untrack(() => statePageParams.value);
    const curPop = untrack(() => statePageParams.popVar);
    const nextVal = values.includes(curVal) ? curVal : (values[0] ?? "av");
    const pops = popVarsFor(nextVal);
    const nextPop =
      pops.length === 0 || pops.includes(curPop) ? curPop : pops[0];
    if (nextVal !== curVal) statePageParams.value = nextVal;
    if (nextPop !== curPop) statePageParams.popVar = nextPop;
  });

  // Reveal page sections hidden by [data-state-loading] once correct values are applied.
  $effect(() => {
    document.documentElement.removeAttribute("data-state-loading");
  });

  // Write URL whenever any relevant state changes (skip first run to let URL read happen first)
  let urlSyncReady = false;
  // Once any non-default setting has appeared, always write all settings (even if reverted to default)
  let settingsWritten = false;
  $effect(() => {
    void [
      selectedYear,
      selectedOffice,
      selectedParty,
      statePageParams.scenario,
      statePageParams.value,
      statePageParams.popVar,
      statePageParams.sort,
      statePageParams.district,
      statePageParams.districtId,
    ];
    if (!urlSyncReady) {
      urlSyncReady = true;
      return;
    }
    syncURL();
  });

  function syncURL() {
    const officeKey = officesByName[selectedOffice] ?? "president";
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.set("election", `${selectedYear}-${officeKey}`);

    if (selectedParty) newUrl.searchParams.set("party", selectedParty);
    else newUrl.searchParams.delete("party");

    if (statePageParams.scenario !== "p2")
      newUrl.searchParams.set("scenario", statePageParams.scenario);
    else newUrl.searchParams.delete("scenario");

    if (statePageParams.district)
      newUrl.searchParams.set("district", statePageParams.district);
    else newUrl.searchParams.delete("district");

    if (statePageParams.districtId)
      newUrl.searchParams.set("districtId", statePageParams.districtId);
    else newUrl.searchParams.delete("districtId");

    const defPop = defaultPopVar[statePageParams.value];
    const hasNonDefault =
      statePageParams.value !== defaultValue ||
      (defPop != null && statePageParams.popVar !== defPop) ||
      statePageParams.sort !== "alpha";
    if (hasNonDefault) settingsWritten = true;

    if (settingsWritten) {
      newUrl.searchParams.set("value", statePageParams.value);
      if (defPop != null)
        newUrl.searchParams.set("pop", statePageParams.popVar);
      else newUrl.searchParams.delete("pop");
      if (statePageParams.sort !== "alpha")
        newUrl.searchParams.set("sort", statePageParams.sort);
      else newUrl.searchParams.delete("sort");
    } else {
      newUrl.searchParams.delete("value");
      newUrl.searchParams.delete("pop");
      newUrl.searchParams.delete("sort");
    }

    window.history.replaceState({}, "", newUrl);
  }
</script>

<div class="state-page__controls">
  <Select
    bind:value={selectedYear}
    options={years.map((y) => ({ value: String(y), label: String(y) }))}
  />
  <Select
    bind:value={selectedOffice}
    options={offices.map((o) => ({
      value: o,
      label: o,
      disabled: o === "House" || o === "Senate",
    }))}
    style="min-width: 6.5rem"
  />
  {#if showDistrictIdSelector}
    <Select
      bind:value={statePageParams.districtId}
      disabled={districtIdSelectorDisabled}
      options={[
        { value: "", label: "All Districts" },
        ...availableDistrictIds.map((d) => ({
          value: d,
          label: `District ${d}`,
        })),
      ]}
      style="min-width: 7rem"
    />
  {/if}
  <Select
    bind:value={selectedParty}
    options={[
      { value: undefined, label: "Any Party" },
      ...PARTIES.map((p) => ({ value: p, label: p })),
    ]}
    style="min-width: 6.5rem"
  />
</div>

<style lang="scss">
  .state-page__controls {
    display: flex;
    gap: 0.4rem;
    align-items: center;
  }

  @media (max-width: 768px) {
    .state-page__controls {
      width: 100%;
      flex-wrap: wrap;
    }
  }
</style>
