<script lang="ts">
  let { text, description, href }: { text: string; description: string; href: string } = $props()
</script>

<span class="info-link-wrap">
  <a class="info-link" {href}>{text}<span class="info-link__tooltip" role="tooltip">{description}</span></a>
</span>

<style lang="scss">
  @use "../styles/variables.scss";

  .info-link-wrap {
    position: relative;
    display: inline-block;
  }

  .info-link {
    color: inherit;
    text-decoration: none;
    border-bottom: 1px dotted currentColor;
    cursor: pointer;

    &:hover {
      border-bottom-color: variables.$dark-gray;
    }
  }

  .info-link__tooltip {
    display: none;
    position: absolute;
    bottom: calc(100% + 6px);
    left: 50%;
    transform: translateX(-50%);
    width: 220px;
    background: #2d2d2d;
    color: #fff;
    font-size: 0.75rem;
    line-height: 1.5;
    padding: 7px 10px;
    border-radius: 5px;
    text-align: left;
    pointer-events: none;
    z-index: 1000;
    white-space: normal;
    font-weight: normal;
    font-style: normal;

    &::after {
      content: '';
      position: absolute;
      top: 100%;
      left: 50%;
      transform: translateX(-50%);
      border: 5px solid transparent;
      border-top-color: #2d2d2d;
    }
  }

  .info-link:hover .info-link__tooltip {
    display: block;
  }
</style>
