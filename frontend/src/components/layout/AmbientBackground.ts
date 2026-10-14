/** Decorative pastel layers; never intercept input or enter the accessibility tree. */
export function ambientBackgroundTemplate(): string {
    return `<div class="ambient" aria-hidden="true">
      <div class="ambient-orb ambient-blue"></div>
      <div class="ambient-orb ambient-lilac"></div>
      <div class="ambient-orb ambient-mint"></div>
      <div class="ambient-orb ambient-rose"></div>
      <div class="ambient-ribbon"></div>
    </div>`;
}
