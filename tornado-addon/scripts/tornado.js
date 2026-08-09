import { world, system, EntityComponentTypes } from "@minecraft/server";

// ---- Configuration ----
const ROD_ID = "minecraft:blaze_rod";   // the item players must hold
const ROD_NAME = "Tornado Rod";         // custom name given to the rod
const PARTICLE = "minecraft:cloud";     // try "minecraft:large_smoke" for a dustier look
const LAYERS = 18;                      // tornado height in blocks
const BASE_RADIUS = 0.4;                // radius at the bottom
const RADIUS_PER_LAYER = 0.45;          // how fast it widens (cone shape)
const POINTS_PER_LAYER = 8;             // particle density per ring
const SPIN = 0.35;                      // rotation speed (radians per tick)
const SUCTION_RADIUS = 6;               // how far the tornado lifts mobs

let angle = 0;

// Returns true if the player is holding the named Tornado Rod in their main hand.
function isHoldingRod(player) {
  const inv = player.getComponent(EntityComponentTypes.Inventory);
  if (!inv || !inv.container) return false;
  const slot = (typeof player.selectedSlot === "number") ? player.selectedSlot : 0;
  const item = inv.container.getItem(slot);
  if (!item) return false;
  if (item.typeId !== ROD_ID) return false;
  // Match by name if the custom name is present, otherwise accept any blaze rod.
  if (item.nameTag) return item.nameTag.includes("Tornado");
  return true;
}

// Main loop: runs every tick, one tornado per holder.
system.runInterval(() => {
  angle = (angle + SPIN) % (Math.PI * 2);

  for (const player of world.getAllPlayers()) {
    if (!isHoldingRod(player)) continue;

    const dim = player.dimension;
    const px = player.location.x;
    const py = player.location.y;
    const pz = player.location.z;

    // Build the rotating cone of particles.
    for (let h = 0; h <= LAYERS; h++) {
      const radius = BASE_RADIUS + h * RADIUS_PER_LAYER;
      const y = py + h;
      for (let p = 0; p < POINTS_PER_LAYER; p++) {
        const a = angle + h * 0.5 + (p * (Math.PI * 2 / POINTS_PER_LAYER));
        const x = px + Math.cos(a) * radius;
        const z = pz + Math.sin(a) * radius;
        try {
          dim.spawnParticle(PARTICLE, { x, y, z });
        } catch (e) { /* chunk not loaded, ignore */ }
      }
    }

    // Suck nearby mobs upward for the "tornado" feel.
    try {
      player.runCommandAsync(
        "effect @e[type=!player,r=" + SUCTION_RADIUS + "] levitation 1 1 true"
      );
    } catch (e) { /* ignore */ }
  }
}, 1);

// Give the Tornado Rod to everyone by running:  /scriptevent tornado:give
system.beforeEvents.scriptEventReceive.subscribe((event) => {
  if (event.id !== "tornado:give") return;
  for (const player of world.getAllPlayers()) {
    try {
      player.runCommandAsync(
        'give @s blaze_rod 1 0 {"minecraft:item_name":"\\"Tornado Rod\\"","minecraft:keep_on_death":{}}'
      );
    } catch (e) { /* ignore */ }
  }
});
