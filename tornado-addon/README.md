# Tornado Rod Add-On (Minecraft Bedrock)

An add-on for a Bedrock (BDS) server — e.g. Aternos — that automatically spawns a
**giant rotating tornado** around any player who is **holding the "Tornado Rod"**.
No command blocks, no structure building, and (after install) no typing on a controller.

## How it works
- A script runs every game tick and checks each player's main hand.
- If a player holds a `blaze_rod` named **Tornado Rod**, a cone of `minecraft:cloud`
  particles is drawn around them, rotating smoothly (real sine/cosine math in JS).
- Nearby mobs get `levitation` so they're sucked up into the funnel.
- Everything is computed in the script — there are no command blocks to place or fill.

## Install on Aternos (file manager)
1. Zip this `tornado-addon` folder (keep `manifest.json` at the root of the zip).
2. In the Aternos panel, open the **Files** / file manager and go to your world folder,
   usually: `worlds/Bedrock level/`
3. Put the pack into: `worlds/Bedrock level/behavior_packs/tornado-addon/`
   (so you have `.../behavior_packs/tornado-addon/manifest.json`).
4. Edit `worlds/Bedrock level/world_behavior_packs.json` and add the pack entry:
   ```json
   [
     { "pack_id": "99306cd0-c403-481f-9c52-e9d67bea7e20", "version": [1, 0, 0] }
   ]
   ```
   (merge with any existing entries; it is a JSON array.)
5. Restart the server. Make sure the world has the add-on enabled
   (Aternos usually enables it automatically once referenced; if scripts don't run,
   enable "Beta APIs" / scripting in the world settings).

## Usage (in-game, as op)
Give the rod to everyone (one command):
```
/scriptevent tornado:give
```
Then any player who **holds the Tornado Rod** gets a tornado around them.
Drop or switch the item and the tornado stops.

## Tuning
Open `scripts/tornado.js` and edit the constants at the top:
- `LAYERS` — tornado height
- `RADIUS_PER_LAYER` — how wide the funnel gets
- `POINTS_PER_LAYER` — particle density (lower it if it lags)
- `SPIN` — rotation speed
- `PARTICLE` — e.g. `"minecraft:large_smoke"` or `"minecraft:white_smoke"`
- `SUCTION_RADIUS` — how far mobs are lifted

## Optional: turn it into a spawnable "structure"
If you still want a `/structure`-style spawn, build the command-block machine once in
a creative test world, run `/structure save tornado_kit <from> <to> disk`, then place
the exported `tornado_kit.mcstructure` into `tornado-addon/structures/` of this pack.
It will then be loadable in-game as `mystructure:tornado_kit` (or via the pack folder
name as the namespace). The script above is the zero-build alternative and is enabled
by default.
