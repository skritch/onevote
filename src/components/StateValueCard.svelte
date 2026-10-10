<script lang="ts">
  import type { ValueType, PopVar, Scenario } from "../lib/values.js";
  import { getStateValue, getDistrictDimension } from "../lib/values.js";
  import { dimensionsStateWinner } from "../lib/elections.js";
  import type { StatePO } from "../lib/states.js";
  import type { Office } from "../lib/elections.js";
  import {
    scenarioNames,
    scenarioDescriptions,
    valueNames,
    valueDescriptions,
    validPopVars,
  } from "../lib/manifest.js";
  import InfoLink from "./InfoLink.svelte";
  import { PARTIES, type Party } from "../lib/party.js";
  import { initCap } from "../utils/strings.js";

  type Props = {
    stateName: string;
    statePO: StatePO;
    scenario: Scenario;
    year: number;
    office: Office;
    value: ValueType;
    popVar: PopVar;
    party?: Party;
    district?: string;
    districtId?: string;
  };

  let {
    stateName,
    statePO,
    scenario,
    year,
    office,
    value,
    popVar,
    party,
    district,
    districtId,
  }: Props = $props();

  const CURRENT_YEAR = new Date().getFullYear();

  const isRealOutcome = $derived((scenario as string) === "p3");
  const isFuture = $derived(year > CURRENT_YEAR);
  const isWVV = $derived(value === "wvv");

  const tense = $derived(
    isRealOutcome
      ? isFuture
        ? "will be"
        : "was"
      : isFuture
        ? "will be"
        : "would have been",
  );

  // For P3 with a district, use district-level winner — ME-2 and NE-2 differ from their state.
  const winningParty = $derived.by((): Party | null => {
    const stateWinner = dimensionsStateWinner[String(year)]?.[statePO] ?? null;
    if (scenario === "p3" && districtId) {
      const distDim = getDistrictDimension(year, statePO, districtId);
      return distDim?.winningParty ?? stateWinner;
    }
    return stateWinner;
  });

  // party prop is title-cased ("Democrat"); normalize to lowercase for comparison
  const selectedPartyKey = $derived(party ? party.toLowerCase() : null);

  // For WVV with no party selected, auto-use the winning party
  const effectivePartyKey = $derived(
    isWVV && !selectedPartyKey ? winningParty : selectedPartyKey,
  );

  const effectiveDistrict = $derived(
    scenario === "p3" || scenario === "p4"
      ? districtId || district || undefined
      : district || undefined,
  );

  const effectivePopVar = $derived(
    (validPopVars[value] ?? []).length > 0 ? popVar : undefined,
  );

  // For WVV, read the party-specific column from data (includes 0 for losing parties).
  const stateValue = $derived(
    getStateValue(
      scenario,
      year,
      statePO,
      value,
      effectivePopVar,
      effectiveDistrict,
      isWVV ? (effectivePartyKey ?? undefined) : undefined,
    ),
  );

  const displayValue = $derived(stateValue);

  // Build a list of parties not being shown in the main display (for the WVV note)
  const wvvOtherParties = $derived.by(() => {
    if (!isWVV || !winningParty)
      return [] as Array<{
        label: string;
        apostrophe: boolean;
        value: number | null;
        isWinner: boolean;
      }>;
    return PARTIES.filter((p) => p.toLowerCase() !== effectivePartyKey).map(
      (p) => ({
        label: p === "Other" ? "third party" : p,
        apostrophe: p !== "Other",
        value: getStateValue(
          scenario,
          year,
          statePO,
          value,
          effectivePopVar,
          effectiveDistrict,
          p.toLowerCase(),
        ),
        isWinner: p.toLowerCase() === winningParty,
      }),
    );
  });

  function districtLabel(d: string): string {
    if (d.toUpperCase() === "AL") return "at-large";
    const n = parseInt(d);
    if (isNaN(n)) return d;
    const suffix = n === 1 ? "st" : n === 2 ? "nd" : n === 3 ? "rd" : "th";
    return `${n}${suffix}`;
  }

  const locationLabel = $derived(
    districtId
      ? `${stateName}'s ${districtLabel(districtId)} district`
      : stateName,
  );

  function formatValue(v: number): string {
    if (v === 0) return "0";
    const s = v.toFixed(2);
    return s;
  }
</script>

<div class="value-card">
  <p class="subject">
    in <strong>{year}</strong>, the value of
    {#if isWVV && effectivePartyKey}
      {#if effectivePartyKey === "other"}
        a <strong>Third Party</strong> vote in <strong>{locationLabel}</strong>
      {:else}
        a <strong>{initCap(effectivePartyKey)}'s</strong>
        vote in <strong>{locationLabel}</strong>
      {/if}
    {:else if party}
      {#if party === "Other"}
        a <strong>Third Party</strong> vote in <strong>{locationLabel}</strong>
      {:else}
        a <strong>{party}'s</strong> vote in
        <strong>{locationLabel}</strong>
      {/if}
    {:else}
      a vote in <strong>{locationLabel}</strong>
    {/if}
    {tense}
  </p>

  {#if displayValue !== null}
    <p class="value">{formatValue(displayValue)}</p>
  {:else}
    <p class="value value--empty">—</p>
  {/if}

  <!-- {#if displayValue !== 0 && displayValue !== null}
    {displayValue > 1 ? "times more than" : "as much as"} the nationwide average
  {/if} -->
  <p class="relative-label">compared to a nationwide average of 1.00</p>
  <div class="sep" aria-hidden="true">—</div>

  {#if !isRealOutcome}
    <p class="scenario">
      in a <InfoLink
        text={scenarioNames[scenario]}
        description={scenarioDescriptions[scenario]}
        href={`${import.meta.env.BASE_URL}about/scenarios/`}
      /> scenario
    </p>
  {/if}

  <p class="value-type">
    as determined by <InfoLink
      text={valueNames[value]}
      description={valueDescriptions[value]}
      href={`${import.meta.env.BASE_URL}about/values/`}
    />
  </p>

  {#if wvvOtherParties.length > 0}
    <div class="sep" aria-hidden="true">—</div>
    <div class="wvv-others">
      {#each wvvOtherParties as other}
        <p class="wvv-other">
          A {other.label}{other.apostrophe ? "'s" : ""}
          vote {tense} worth
          <strong
            >{other.value !== null ? formatValue(other.value) : "—"}</strong
          >
        </p>
      {/each}
    </div>
  {/if}
</div>

<style lang="scss">
  @use "../styles/variables.scss";

  .value-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: variables.$spacing-sm variables.$spacing-md;
    background: variables.$white;
    border: 1px solid #e5e7eb;
    border-radius: variables.$border-radius;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.07);
    text-align: center;
  }

  .subject {
    strong {
      color: variables.$dark-gray;
    }
  }

  .value {
    font-size: 3.2rem;
    font-weight: 700;
    color: variables.$dark-gray;

    &--empty {
      color: variables.$medium-gray;
    }
  }

  .sep {
    font-size: 0.6rem;
    line-height: 1;
    color: #c8ccd0;
    margin: -0.15rem 0;
    user-select: none;
  }
  .value-type {
    font-size: 0.72rem;
    color: variables.$medium-gray;
  }

  .scenario {
    font-size: 0.72rem;
    color: variables.$medium-gray;
  }

  .wvv-others {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.15rem;
  }

  .wvv-other {
    font-size: 0.72rem;
    color: variables.$medium-gray;

    strong {
      color: variables.$dark-gray;
    }
  }
</style>
