<script lang="ts">
  import { untrack } from "svelte";
  import type { CompareStatesParams } from "./CompareStatesPage.svelte";
  import type { State } from "../../lib/states.js";
  import type { DistrictIndex } from "../../lib/districts.js";
  import { getDistrictIdsForYear } from "../../lib/districts.js";
  import { OFFICES } from "../../lib/elections.js";
  import { initCap } from "../../utils/strings.js";
  import { PARTIES, partyShortNames } from "../../lib/party.js";
  import type { Party } from "../../lib/party.js";
  import Select from "../Select.svelte";
  import SettingsPanel from "../SettingsPanel.svelte";

  type Props = {
    years: number[];
    states: State[];
    districtIndex: Record<string, DistrictIndex>;
    params: CompareStatesParams;
  };

  let { years, states, districtIndex, params }: Props = $props();

  // ── District availability ────────────────────────────────────────────────

  function availableDistricts(statePO: string): string[] {
    if (!districtIndex[statePO]) return [];
    return getDistrictIdsForYear(statePO, params.year);
  }

  function districtDisabled(statePO: string): boolean {
    const ids = availableDistricts(statePO);
    return (
      ids.length === 0 ||
      (ids.length === 1 && ids[0] === "AL") ||
      params.year < 2012
    );
  }

  const districts1 = $derived(availableDistricts(params.state1));
  const districts2 = $derived(availableDistricts(params.state2));
  const districtDisabled1 = $derived(districtDisabled(params.state1));
  const districtDisabled2 = $derived(districtDisabled(params.state2));

  // Reset district when state or year changes and selection is no longer valid.
  $effect(() => {
    const available = districts1;
    const cur = untrack(() => params.district1);
    if (cur && !available.includes(cur)) untrack(() => { params.district1 = ""; });
  });
  $effect(() => {
    const available = districts2;
    const cur = untrack(() => params.district2);
    if (cur && !available.includes(cur)) untrack(() => { params.district2 = ""; });
  });

  // ── Party auto-sync ──────────────────────────────────────────────────────

  function opposite(party: string): string {
    if (party === "Democrat") return "Republican";
    if (party === "Republican") return "Democrat";
    return "Republican"; // Other → Republican
  }

  // Plain (non-reactive) vars to track previous values so we can distinguish
  // "user just cleared a party" from "party was always empty."
  let prevParty1 = untrack(() => params.party1);
  let prevParty2 = untrack(() => params.party2);

  $effect(() => {
    const s1 = params.state1;
    const s2 = params.state2;
    const p1 = params.party1;
    const p2 = params.party2;

    const prev1 = prevParty1;
    const prev2 = prevParty2;
    prevParty1 = p1;
    prevParty2 = p2;

    // Same state + same/no party → force D vs R.
    if (s1 && s2 && s1 === s2 && p1 === p2) {
      untrack(() => { params.party1 = "Democrat"; params.party2 = "Republican"; });
      return;
    }
    // "Any Party" is contagious — but only when explicitly cleared (was set before).
    if (!p1 && prev1 && p2) {
      untrack(() => { params.party2 = ""; });
      return;
    }
    if (!p2 && prev2 && p1) {
      untrack(() => { params.party1 = ""; });
      return;
    }
    // One set, other empty → fill with opposite.
    if (p1 && !p2) untrack(() => { params.party2 = opposite(p1); });
    else if (p2 && !p1) untrack(() => { params.party1 = opposite(p2); });
  });

  // ── Title ────────────────────────────────────────────────────────────────

  function partyAbbr(party: string): string {
    if (party === "Democrat") return "(D)";
    if (party === "Republican") return "(R)";
    if (party === "Other") return "(3P)";
    return "";
  }

  function districtSuffix(district: string): string {
    return district && district !== "AL" ? `-${district}` : "";
  }

  const title = $derived.by(() => {
    const name1 = states.find((s) => s.statePO === params.state1)?.stateName;
    const name2 = states.find((s) => s.statePO === params.state2)?.stateName;
    const tag1 = params.party1 ? ` ${partyAbbr(params.party1)}` : "";
    const tag2 = params.party2 ? ` ${partyAbbr(params.party2)}` : "";
    const label1 = name1 ? `${name1}${districtSuffix(params.district1)}${tag1}` : null;
    const label2 = name2 ? `${name2}${districtSuffix(params.district2)}${tag2}` : null;
    if (label1 && label2) return `${label1} vs. ${label2}`;
    if (label1) return `${label1} vs. ...`;
    if (label2) return `... vs. ${label2}`;
    return "Comparing States";
  });

</script>

<div class="compare-controls">
  <h1 class="compare-controls__title">{title}</h1>
  <div class="compare-controls__toolbar">
    <Select
      bind:value={params.year}
      options={years.map((y) => ({ value: y, label: String(y) }))}
    />
    <Select
      bind:value={params.office}
      options={OFFICES.map((o) => ({
        value: o,
        label: initCap(o),
        disabled: o !== "president",
      }))}
      style="min-width: 6.5rem"
    />
    <SettingsPanel
      year={params.year}
      bind:value={params.value}
      bind:popVar={params.popVar}
      bind:scenario={params.scenario}
    />
  </div>

  <div class="compare-controls__bar">
    <div class="compare-controls__group">
      <Select
        bind:value={params.state1}
        options={[
          { value: "", label: "-- State --" },
          ...states.map((s) => ({ value: s.statePO, label: s.stateName })),
        ]}
      />
      <Select
        bind:value={params.district1}
        disabled={districtDisabled1}
        options={[
          { value: "", label: "Any District" },
          ...districts1.filter((d) => d !== "AL").map((d) => ({ value: d, label: `District ${d}` })),
        ]}
      />
      <Select
        bind:value={params.party1}
        triggerLabel={params.party1 ? partyShortNames[params.party1 as Party] : undefined}
        options={[
          { value: "", label: "Any Party" },
          ...PARTIES.map((p) => ({ value: p, label: p })),
        ]}
      />
    </div>

    <span class="compare-controls__vs" aria-hidden="true">vs.</span>

    <div class="compare-controls__group">
      <Select
        bind:value={params.state2}
        options={[
          { value: "", label: "-- State --" },
          ...states.map((s) => ({ value: s.statePO, label: s.stateName })),
        ]}
      />
      <Select
        bind:value={params.district2}
        disabled={districtDisabled2}
        options={[
          { value: "", label: "Any District" },
          ...districts2.filter((d) => d !== "AL").map((d) => ({ value: d, label: `District ${d}` })),
        ]}
      />
      <Select
        bind:value={params.party2}
        triggerLabel={params.party2 ? partyShortNames[params.party2 as Party] : undefined}
        options={[
          { value: "", label: "Any Party" },
          ...PARTIES.map((p) => ({ value: p, label: p })),
        ]}
      />
    </div>
  </div>
</div>

<style lang="scss">
  @use "../../styles/variables.scss";

  .compare-controls {
    display: grid;
    grid-template-areas: "title toolbar" "bar bar";
    grid-template-columns: 1fr auto;
    gap: variables.$spacing-xs;
    margin-bottom: variables.$spacing-lg;

    &__title {
      grid-area: title;
      align-self: center;
      font-size: variables.$font-size-large;
      font-weight: 700;
      color: variables.$dark-gray;
      margin: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    &__toolbar {
      grid-area: toolbar;
      display: flex;
      align-items: center;
      gap: variables.$spacing-xs;
    }

    &__bar {
      grid-area: bar;
      display: flex;
      align-items: center;
      gap: variables.$spacing-sm;
      padding: variables.$spacing-sm variables.$spacing-md;
      background: variables.$white;
      border: 1px solid #e5e7eb;
      border-radius: variables.$border-radius;
    }

    &__group {
      display: flex;
      align-items: center;
      gap: variables.$spacing-xs;
      flex: 1;
      min-width: 0;

      // Let Select components shrink within the group.
      :global(.cs) {
        flex: 1 1 0;
        min-width: 0;
      }
    }

    &__vs {
      font-size: variables.$font-size-small;
      color: variables.$medium-gray;
      flex-shrink: 0;
    }

    @media (max-width: 700px) {
      grid-template-areas: "title" "bar" "toolbar";
      grid-template-columns: 1fr;

      &__toolbar {
        justify-content: flex-end;
      }

      &__bar {
        flex-wrap: wrap;
      }

      &__group {
        flex: 1 0 100%;

        :global(.cs) {
          flex: 1 1 auto;
        }
      }

      &__vs {
        display: none;
      }
    }
  }
</style>
