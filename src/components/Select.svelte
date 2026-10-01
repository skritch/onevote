<script lang="ts">
  let {
    options,
    value = $bindable(''),
    triggerLabel,
    style = '',
  }: {
    options: { value: string; label: string; disabled?: boolean }[];
    value?: string;
    triggerLabel?: string;
    style?: string;
  } = $props();

  let open = $state(false);
  let el: HTMLDivElement | undefined;

  const selectedLabel = $derived(
    triggerLabel ?? options.find(o => o.value === value)?.label ?? '—'
  );

  function handlePointerDown(e: PointerEvent) {
    if (open && el && !el.contains(e.target as Node)) {
      open = false;
    }
  }

  // Dispatch ui:close when dropdown closes so ElectionPlot can close tooltips
  $effect(() => {
    if (!open) return;
    return () => { document.dispatchEvent(new CustomEvent('ui:close')); };
  });
</script>

<svelte:window onpointerdown={handlePointerDown} />

<div class="cs" bind:this={el} {style}>
  <button
    class="cs__trigger"
    class:open
    onclick={() => (open = !open)}
  >
    <span class="cs__label">{selectedLabel}</span>
    <span class="cs__arrow" class:open>▾</span>
  </button>
  {#if open}
    <div class="cs__list">
      {#each options as opt}
        <button
          class="cs__option"
          class:selected={opt.value === value}
          disabled={opt.disabled}
          onmousedown={(e) => { e.preventDefault(); value = opt.value; open = false; }}
        >
          {opt.label}
        </button>
      {/each}
    </div>
  {/if}
</div>

<style lang="scss">
  @use "../styles/variables.scss";

  .cs {
    position: relative;
    display: inline-block;

    &__trigger {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.4rem;
      width: 100%;
      background: variables.$white;
      border: 1px solid #e0e2e6;
      border-radius: 6px;
      padding: 3px 7px 3px 9px;
      font-size: 0.82rem;
      color: variables.$dark-gray;
      cursor: pointer;
      text-align: left;
      white-space: nowrap;
      transition: border-color 0.1s;

      &:hover, &.open {
        border-color: #9ca3af;
      }

      &:focus {
        outline: none;
        border-color: variables.$royal-blue;
      }
    }

    &__arrow {
      font-size: 0.6rem;
      color: #b0b5be;
      flex-shrink: 0;
      transition: transform 0.15s;
      line-height: 1;

      &.open {
        transform: rotate(180deg);
      }
    }

    &__list {
      position: absolute;
      top: calc(100% + 4px);
      left: 0;
      min-width: 100%;
      width: max-content;
      background: variables.$white;
      border: 1px solid #e0e2e6;
      border-radius: 6px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.10);
      z-index: 400;
      padding: 4px 0;
      max-height: 18rem;
      overflow-y: auto;
    }

    &__option {
      display: block;
      width: 100%;
      padding: 5px 10px;
      font-size: 0.82rem;
      color: variables.$dark-gray;
      background: none;
      border: none;
      text-align: left;
      cursor: pointer;
      white-space: nowrap;

      &:hover:not(:disabled) {
        background: #f7f8f9;
      }

      &:disabled {
        color: #c8cbd0;
        cursor: not-allowed;
      }

      &.selected {
        font-weight: 600;
        color: #111827;
      }
    }
  }
</style>
