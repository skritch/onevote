<script lang="ts">
  import { chartState } from "../lib/chartState.svelte.js";
  import { getStateValue } from "../lib/values.js";
  import {
    scenarioNames,
    scenarioDescriptions,
    valueNames,
    valueDescriptions,
    validPopVars,
  } from "../lib/manifest.js";
  import InfoLink from "./InfoLink.svelte";

  let { stateName, statePo }: { stateName: string; statePo: string } = $props();

  const CURRENT_YEAR = new Date().getFullYear();

  const value = $derived(
    getStateValue(
      chartState.scenario,
      chartState.year,
      statePo.toUpperCase(),
      chartState.value,
      (validPopVars[chartState.value] ?? []).length > 0
        ? chartState.popVar
        : undefined,
    ),
  );

  const isRealOutcome = $derived((chartState.scenario as string) === "p3");
  const isFuture = $derived(chartState.year > CURRENT_YEAR);

  const tense = $derived(
    isRealOutcome
      ? isFuture
        ? "will be"
        : "was"
      : isFuture
        ? "would be"
        : "would have been",
  );

  function formatValue(v: number): string {
    const s = v.toFixed(3);
    return v < 1 ? s.slice(1) : s;
  }
</script>

<div class="value-card">
  <p class="subject">
    in <strong>{chartState.year}</strong>,
    {#if chartState.party}
      {#if chartState.party === "Other"}
        a <strong>Third Party</strong> vote in <strong>{stateName}</strong>
      {:else}
        a <strong>{chartState.party}'s</strong> vote in <strong>{stateName}</strong>
      {/if}
    {:else}
      a vote in <strong>{stateName}</strong>
    {/if}
  </p>

  <p class="tense">{tense} worth</p>

  {#if value !== null}
    <p class="value">{formatValue(value)}</p>
    <p class="votes-label">votes</p>
  {:else}
    <p class="value value--empty">—</p>
  {/if}

  <p class="relative-label">relative to the average American</p>

  <div class="sep" aria-hidden="true">—</div>

  <p class="value-type">
    as determined by <InfoLink
      text={valueNames[chartState.value]}
      description={valueDescriptions[chartState.value]}
      href="/about/definitions"
    />
  </p>

  {#if !isRealOutcome}
    <div class="sep" aria-hidden="true">—</div>
    <p class="scenario">
      in a <InfoLink
        text={scenarioNames[chartState.scenario]}
        description={scenarioDescriptions[chartState.scenario]}
        href="/about/scenarios"
      /> scenario
    </p>
  {/if}
</div>

<style lang="scss">
  @use "../styles/variables.scss";

  .value-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.3rem;
    padding: variables.$spacing-sm variables.$spacing-md;
    background: variables.$white;
    border: 1px solid #e5e7eb;
    border-radius: variables.$border-radius;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.07);
    text-align: center;

    p {
      margin: 0;
    }

    .value {
      margin-top: 1rem;
    }

    .votes-label {
      margin-bottom: 1rem;
    }
  }

  .subject {
    font-size: 1.2rem;
    color: variables.$medium-gray;
    line-height: 1.4;

    strong {
      color: variables.$dark-gray;
    }
  }

  .tense {
    font-size: 0.75rem;
    color: variables.$medium-gray;
  }

  .value {
    font-size: 3.2rem;
    font-weight: 700;
    color: variables.$dark-gray;
    line-height: 1;

    &--empty {
      color: variables.$medium-gray;
    }
  }

  .votes-label {
    font-size: 1.3rem;
    color: variables.$medium-gray;
  }

  .sep {
    font-size: 0.6rem;
    line-height: 1;
    color: #c8ccd0;
    margin: -0.15rem 0;
    user-select: none;
  }

  .relative-label {
    font-size: 0.75rem;
    color: variables.$medium-gray;
  }

  .value-type {
    font-size: 0.72rem;
    color: variables.$medium-gray;
  }

  .scenario {
    font-size: 0.72rem;
    color: variables.$medium-gray;
  }
</style>
