---
name: minecraft-client-to-server-conversion
category: software-development
description: Convert client modpack to server, filter client-only mods.
---

# Minecraft Client to Server Conversion

Convert a modded Minecraft client installation into a dedicated server by identifying and migrating server-compatible mods while filtering out client-only content.

## When to Use

- User wants to create a server from an existing client modpack
- Need to analyze mod compatibility between client and server
- Migrating a working client setup to dedicated server
- Auditing server mods against client installation

## Workflow

### 1. Identify Client and Server Paths

```bash
# Client path (usually in launcher directory)
CLIENT="/path/to/.minecraft/versions/<pack_name>/mods/"

# Server path
SERVER="/path/to/server/<pack_name>/mods/"
```

### 2. Count and Compare Mods

```bash
ls "$CLIENT" | wc -l  # Client mod count
ls "$SERVER" | wc -l  # Server mod count

# List mods only in client
comm -23 <(ls "$CLIENT" | sort) <(ls "$SERVER" | sort)
```

### 3. Categorize Client-Only Mods

**Always Client-Only (Never copy to server):**

**Rendering & Performance:**
- Sodium / Embeddium / Rubidium (+ variants: extra, plus)
- Iris / Oculus (shaders)
- OptiFine
- Shader mods (Canvas, etc.)
- GPU fixes (gpumemleakfix, etc.)
- Fog/particle renderers

**UI & Menus:**
- Main menu customizers (PackMenu, FancyMenu, CustomMainMenu)
- HUD mods (JourneyMap minimap, Xaero's Minimap, AppleSkin)
- Inventory tweaks UI (MouseTweaks, InventoryTweaks)
- Chat UI (BetterChat, ChatUp)
- ModernUI, BetterThirdPerson

**Input & Client Interaction:**
- IME/input method mods (IMBlocker, jecharacters)
- Keybind mods (unless server-synced)
- Camera/perspective mods
- Replay Mod

**Audio:**
- Sound filters (ExtremeSoundMuffler, Sound Reloader)
- Music mods

**Resource/Texture Related:**
- CTM (Connected Textures Mod)
- Entity Texture Features
- Animated textures (unless data-driven)

### 4. Identify Server-Compatible Mods

**Should Copy to Server:**

**Information Display (with server sync):**
- Jade / WTHIT / WAILA (syncs block NBT data)
- The One Probe (TOP)

**Recipe/Info Mods:**
- JEI (Just Enough Items) - optional but recommended for recipe sync
- JEI Integration
- Just Enough Resources (JER) - syncs world gen data

**Gameplay/Mechanics (if present):**
- Any mod that adds blocks, items, or mechanics
- World generation mods
- Dimension mods
- Quest mods (FTB Quests, etc.)
- Chunk loaders
- Team/party systems

**Library/API Mods:**
- Architectury, Forge/Fabric API
- KubeJS, CraftTweaker
- ContentTweaker, Custom machinery
- Library mods marked as "both sides" or "universal"

**Check Carefully (mod-dependent):**
- ModernUI (if marked universal, may have server components)
- Server-side inventory management (if client has inventory tweaks with server sync)

### 5. Copy Server-Compatible Mods

```bash
# Copy individual identified mods
cp "$CLIENT/ModName.jar" "$SERVER/"

# Verify copy
ls -lh "$SERVER/ModName.jar"
```

### 6. Document Changes

Create a summary:
```
Client mods: X
Server mods: Y
Added: Z mods
  - ModA (reason)
  - ModB (reason)
Skipped: N mods (all client-only rendering/UI)
```

## Decision Tree

```
For each mod in client but not in server:
  - Is it rendering/shaders/GPU? -> SKIP (client-only)
  - Is it UI/menu/HUD? -> SKIP (client-only)
  - Is it input/IME/sound? -> SKIP (client-only)
  - Does it display server data (Jade, JER)? -> COPY (needs server sync)
  - Does it add gameplay content? -> COPY (required for mechanics)
  - Is it marked universal or both? -> CHECK mod page, usually COPY
  - Unsure? -> Check mod page for server required / client only tags
```

## Common Patterns

**GTL/GregTech packs:**
- Copy: JEI, Jade, JER (data sync improves experience)
- Skip: Embeddium, Oculus, ModernUI, MouseTweaks

**FTB packs:**
- Copy: FTB mods (Quests, Teams, Chunks - all require server)
- Skip: PackMenu, client resource pack mods

**Create modpacks:**
- Copy: Create (obviously), Flywheel (rendering lib but required server-side)
- Skip: Oculus/shader pipeline mods

## Verification

After copying:
```bash
# Check server will load new mods (dry run if possible)
./start.sh --dry-run  # or check logs on next boot

# Common signs of client-only mod on server:
# - NoClassDefFoundError: net/minecraft/client/...
# - sided annotation mismatch
```

## Pitfalls

- Do not assume optional means client-only - Jade is optional but improves server function
- Do not copy performance mods - Embeddium/Sodium break servers or do nothing
- Check dependencies - If copying JEI Integration, ensure JEI is also present
- Restart required - Server must restart to load new mods

## Example GTL Case

**Client: 85 mods | Server: 67 mods | Gap: 18 mods**

**Analysis:**
- Copied: YSM (player models sync), JEI, Jade, JEI Integration, JER (5 mods)
- Skipped: embeddium, oculus, rubidium-extra, Shimmer, gpumemleakfix, IMBlocker, jecharacters, ModernUI, MouseTweaks, PackMenu, invtweaks, ExtremeSoundMuffler (12 client-only)
- Result: Server 67->72, client-server gap reduced from 18 to 13 (all remaining are valid client-only)

## References

- Mod pages usually tag Client / Server / Both
- CurseForge/Modrinth mod environment badges
- Forge @OnlyIn annotations in crash logs reveal sided mods
