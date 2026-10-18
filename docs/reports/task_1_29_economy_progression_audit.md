# Task 1.29 — Pet Collection Progression & Reward Balance Audit Report

## Executive Summary

Task 1.29 is an audit of the progression, economy, and reward balance in **Pet Mining Empire**. The audit investigated whether players can earn coins, purchase equipment upgrades, hatch eggs, and benefit from their companions at a reasonable and satisfying pace.

All findings are based on inspection of the codebase on disk and in the active Roblox Studio session, verified through theoretical modeling and empirical measurements conducted in **Roblox Studio Play Mode** (`Studio ID: 416e11ba-e05b-4e9c-b7b0-04f7f7283c5f`).

### Key Findings at a Glance

1. **Early-Game Pacing is Fast and Rewarding**:
   - A single full clear of Stage 1 quarry nodes (12 nodes, ~21-25 ores) yields **~97 to 131 Coins** in **~32.6 seconds** of active mining.
   - The first essential upgrade, **Reinforced Iron Pickaxe** (Cost: 100 Coins, 2x power), is attainable on **Trip #1** (~45 seconds of gameplay).
   - The **Common Quarry Egg** (Cost: 250 Coins) requires **2 trips** with starter equipment, or **exactly 1 trip** once the player upgrades to the Tier 2 Backpack (50 capacity).

2. **The "Quantized Cadence" Effect on Companions**:
   - Pet assists are evaluated server-authoritatively inside `MiningService:ProcessMineRequest`, which fires at most once every **0.5s** (the manual swing cooldown).
   - Under continuous manual swinging at maximum rate:
     - **Scrap Kitty** (0.8s cooldown) only triggers at \( t = 0.0s, 1.0s, 2.0s \dots \), resulting in an effective **1.0s interval** (identical to Rusty Pup).
     - **Iron Mole** (1.2s cooldown, 3 DMG) triggers at \( t = 0.0s, 1.5s, 3.0s \dots \), resulting in an effective **1.5s interval**.
     - All three companions produce an identical effective assist throughput of **2.0 DPS** during uninterrupted maximum-rate swinging.

3. **Stage 1 Breakpoint Overshoot**:
   - Because Stage 1 node HP values are exact multiples of 30 (Stone: 30 HP, Copper: 60 HP, Coal: 90 HP) and the Starter Pickaxe deals 10 damage, the +2 assist damage from Rusty Pup/Scrap Kitty leaves nodes at 8, 4, and 2 HP just before the final swing. Consequently, the pet assist does not save a swing on these specific nodes when using the Starter Pickaxe alone.
   - However, on uneven HP or higher tier nodes (Stage 2 Iron: 150 HP, Gold: 240 HP, Cyanite: 350 HP), and especially when paired with the Tier 2 Pickaxe (20 Power), companions contribute directly to reducing total swing counts.

4. **Security & Boundary Enforcement**:
   - All server validation checks (node existence, interaction reach, swing cooldowns, backpack capacity limits, sell pad proximity, egg station proximity, sequential tier progression, and balance affordability) successfully rejected invalid and exploitative requests.

---

## 1. Authoritative Configuration Values & Formulas Inspected

### A. Ore Configuration (`OreConfig.luau`)

| Ore Type | Cave Stage | Max HP | Hardness | Respawn (s) | Unit Value (Coins) | Base XP | Drop Range | Avg Drop | Avg Coins / Node |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stone** | Stage 1 | 30 | 1 | 6s | 1 | 1 | 1 – 2 | 1.5 | 1.5 Coins |
| **Copper** | Stage 1 | 60 | 2 | 10s | 5 | 3 | 1 – 3 | 2.0 | 10.0 Coins |
| **Coal** | Stage 1 | 90 | 3 | 14s | 12 | 6 | 2 – 4 | 3.0 | 36.0 Coins |
| **Iron** | Stage 2 | 150 | 4 | 12s | 25 | 10 | 2 – 4 | 3.0 | 75.0 Coins |
| **Gold** | Stage 2 | 240 | 5 | 18s | 60 | 20 | 2 – 3 | 2.5 | 150.0 Coins |
| **Cyanite** | Stage 2 | 350 | 6 | 25s | 140 | 35 | 1 – 3 | 2.0 | 280.0 Coins |

### B. Node Spawning in Caves (`MiningService.luau`)

- **Stage 1 (Quarry Sector)**:
  - 6 Stone nodes: \( 6 \times 1.5 = 9 \) Stone (\( 9 \times 1 = 9 \) Coins)
  - 4 Copper nodes: \( 4 \times 2.0 = 8 \) Copper (\( 8 \times 5 = 40 \) Coins)
  - 2 Coal nodes: \( 2 \times 3.0 = 6 \) Coal (\( 6 \times 12 = 72 \) Coins)
  - **Full Clear Total**: 12 nodes, **23 average ores**, **121 Coins total yield**.
  - **Weighted Average Ore Value**: \( 121 / 23 \approx \) **5.26 Coins / ore**.

- **Stage 2 (Cavern Sector)**:
  - 4 Iron nodes: \( 4 \times 3.0 = 12 \) Iron (\( 12 \times 25 = 300 \) Coins)
  - 4 Gold nodes: \( 4 \times 2.5 = 10 \) Gold (\( 10 \times 60 = 600 \) Coins)
  - 4 Cyanite nodes: \( 4 \times 2.0 = 8 \) Cyanite (\( 8 \times 140 = 1,120 \) Coins)
  - **Full Clear Total**: 12 nodes, **30 average ores**, **2,020 Coins total yield**.
  - **Weighted Average Ore Value**: \( 2,020 / 30 \approx \) **67.33 Coins / ore**.

### C. Equipment Progression (`EquipmentConfig.luau`)

#### Pickaxes:
| Tier | Id | Display Name | Level | Mining Power | Cost | Description |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **1** | `RustyPickaxe` | Rusty Pickaxe | 1 | 10 | Free | Novice pickaxe. Baseline 20.0 DPS (manual). |
| **2** | `ReinforcedIronPickaxe` | Reinforced Iron Pickaxe | 2 | 20 | 100 Coins | 2x power. 40.0 DPS (manual). |
| **3** | `SteelPickaxe` | Steel Pickaxe | 3 | 30 | 350 Coins | 3x power. 60.0 DPS (manual). One-shots Stone! |
| **4** | `TemperedPickaxe` | Tempered Pickaxe | 4 | 50 | 900 Coins | 5x power. 100.0 DPS (manual). |
| **5** | `IndustrialDrill` | Industrial Drill | 5 | 100 | 2,500 Coins | 10x power. 200.0 DPS (manual). |

#### Backpacks:
| Tier | Id | Display Name | Level | Capacity | Cost | Description |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **1** | `SmallPouch` | Small Pouch | 1 | 25 | Free | Starter capacity. Holds ~12-14 nodes. |
| **2** | `MiningRucksack` | Mining Rucksack | 2 | 50 | 150 Coins | 2x capacity. Holds full Stage 1 clear. |
| **3** | `ReinforcedHauler` | Reinforced Hauler | 3 | 100 | 500 Coins | 4x capacity. Ideal for Stage 2 cavern runs. |
| **4** | `CargoCrate` | Cargo Crate | 4 | 250 | 1,500 Coins | 10x capacity. Bulk industrial hauls. |

### D. Companion Roster (`PetConfig.luau`)

| Companion | Acquisition Source | Cost / Probability | Mining Power | Assist Cadence | Theoretical Assist DPS | Effective Assist DPS (Continuous Swing) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Rusty Pup** | Starter Grant (Free) | Free (100%) | 2 | 1.0s | 2.0 DPS | 2.0 DPS (\( 2 \text{ DMG} / 1.0\text{s} \)) |
| **Scrap Kitty** | Common Quarry Egg | 250 Coins (60%) | 2 | 0.8s | 2.5 DPS | 2.0 DPS (\( 2 \text{ DMG} / 1.0\text{s} \)) |
| **Iron Mole** | Common Quarry Egg | 250 Coins (40%) | 3 | 1.2s | 2.5 DPS | 2.0 DPS (\( 3 \text{ DMG} / 1.5\text{s} \)) |

---

## 2. Mining Performance & Companion Comparison

### A. Theoretical Hit & Timing Breakdown

When the player holds down or rapidly clicks the mine button, manual swings occur every **0.5s** (\( t = 0.0s, 0.5s, 1.0s, 1.5s, 2.0s \dots \)).

#### Starter Pickaxe (Power 10):
- **Stone (30 HP)**:
  - *No Pet*: \( t=0.0s \) (20 HP) \(\to t=0.5s \) (10 HP) \(\to t=1.0s \) (0 HP) \(\implies\) **3 hits, 1.00s**.
  - *Rusty Pup (2 DMG, 1.0s)*: \( t=0.0s \) (18 HP) \(\to t=0.5s \) (8 HP) \(\to t=1.0s \) (0 HP) \(\implies\) **3 hits, 1.00s**.
  - *Scrap Kitty (2 DMG, 0.8s)*: \( t=0.0s \) (18 HP) \(\to t=0.5s \) (8 HP) \(\to t=1.0s \) (0 HP) \(\implies\) **3 hits, 1.00s**.
  - *Iron Mole (3 DMG, 1.2s)*: \( t=0.0s \) (17 HP) \(\to t=0.5s \) (7 HP) \(\to t=1.0s \) (0 HP) \(\implies\) **3 hits, 1.00s**.

- **Copper (60 HP)**:
  - *No Pet*: \( 60 / 10 = \) **6 hits, 2.50s**.
  - *With Rusty Pup*: Hits deal 12, 10, 12, 10, 12 \(\to\) after 5 hits, 4 HP left \(\to\) **6 hits, 2.50s**.
  - *With Scrap Kitty*: Same 5 hits deal 56 damage (4 HP left) \(\to\) **6 hits, 2.50s**.
  - *With Iron Mole*: Hits deal 13, 10, 10, 13, 10 \(\to\) after 5 hits, 4 HP left \(\to\) **6 hits, 2.50s**.

- **Coal (90 HP)**:
  - *No Pet*: \( 90 / 10 = \) **9 hits, 4.00s**.
  - *With Any Pet*: Total damage through 8 hits is 88 damage (leaving 2 HP) \(\to\) **9 hits, 4.00s**.

### B. Empirical Measurements (Play Mode Telemetry)

The following measurements were captured live in Studio Play mode by automating discrete swings via `MiningService:ProcessMineRequest`:

| Target Ore | Node HP | Companion Loadout | Measured Hits | Measured Time | Measured DPS | Deviation from Theory |
| :--- | :---: | :--- | :---: | :---: | :---: | :--- |
| **Stone** | 30 | None | 3 | 1.07s | 28.0 | +0.07s (Task scheduling delta) |
| **Stone** | 30 | Rusty Pup | 3 | 1.04s | 28.7 | +0.04s |
| **Stone** | 30 | Scrap Kitty | 3 | 1.03s | 29.1 | +0.03s |
| **Stone** | 30 | Iron Mole | 3 | 1.03s | 29.0 | +0.03s |
| **Copper** | 60 | None | 6 | 2.58s | 23.2 | +0.08s |
| **Copper** | 60 | Rusty Pup | 6 | 2.60s | 23.1 | +0.10s |
| **Copper** | 60 | Scrap Kitty | 6 | 2.60s | 23.1 | +0.10s |
| **Copper** | 60 | Iron Mole | 6 | 2.61s | 23.0 | +0.11s |
| **Coal** | 90 | None | 9 | 4.14s | 21.7 | +0.14s |
| **Coal** | 90 | Rusty Pup | 9 | 4.15s | 21.7 | +0.15s |
| **Coal** | 90 | Scrap Kitty | 9 | 4.13s | 21.8 | +0.13s |
| **Coal** | 90 | Iron Mole | 9 | 4.16s | 21.6 | +0.16s |

### C. Tier 2 Pickaxe (Power 20) Benchmark

When the player purchases the **Reinforced Iron Pickaxe** (100 Coins, Power 20), the swing count drops dramatically:

| Target Ore | Node HP | Pickaxe Loadout | Companion | Measured Hits | Measured Time | Measured DPS | Throughput Increase |
| :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **Stone** | 30 | Tier 2 (20 Power) | None | 2 | 0.52s | 57.5 | **+106% faster** (vs Tier 1) |
| **Stone** | 30 | Tier 2 (20 Power) | Iron Mole | 2 | 0.52s | 58.1 | **+108% faster** |
| **Copper** | 60 | Tier 2 (20 Power) | None | 3 | 1.04s | 58.0 | **+148% faster** (down from 2.58s) |
| **Copper** | 60 | Tier 2 (20 Power) | Iron Mole | 3 | 1.05s | 57.2 | **+149% faster** |
| **Coal** | 90 | Tier 2 (20 Power) | None | 5 | 2.07s | 43.6 | **+100% faster** (down from 4.14s) |
| **Coal** | 90 | Tier 2 (20 Power) | Iron Mole | 5 | 2.06s | 43.6 | **+101% faster** |

---

## 3. Trip Economics & Player Progression Modeling

### A. Single Mining Trip Telemetry (Measured in Play Mode)

A standard starter player run was executed from Plot #1 through the Stage 1 Quarry, filling the starter 25-capacity backpack and returning to the Plot Drop-Off Station to sell:

- **Nodes Mined**: 12 nodes (2 Coal, 4 Copper, 6 Stone).
- **Total Swings**: 60 swings.
- **Active Mining Time**: **32.6 seconds**.
- **Ores Gathered**: 21 ores total (4 Coal, 8 Copper, 9 Stone).
- **Selling Payout**: **+97 Coins** credited immediately at base drop-off pad.
- **Full Trip Cycle Time**: **~45 seconds** (including walk from quarry to plot).

### B. Progression Milestones & Trips Required

| Milestone | Item / Unlock | Cost (Coins) | Trips Required (Starter Gear, 25 Cap) | Trips Required (Tier 2 Gear, 50 Cap) | Est. Active Playtime | Evaluation |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **1. First Tool Upgrade** | Reinforced Iron Pickaxe | 100 | **1 trip** (yields 97–121 Coins) | N/A | **~45 seconds** | ⭐ **Excellent**. Instant early gratification. |
| **2. First Bag Upgrade** | Mining Rucksack (Cap 50) | 150 | **2 trips** | N/A | **~1.5 minutes** | ⭐ **Smooth**. Doubles carry limit to 50 ores. |
| **3. First Egg Hatch** | Common Quarry Egg | 250 | **2–3 trips** | **1 trip** (50 cap yields ~263 Coins) | **~3 minutes** | ⭐ **Fair**. Balanced alternative to equipment. |
| **4. Advanced Tool** | Steel Pickaxe (Power 30) | 350 | **3–4 trips** | **1.3 trips** | **~4.5 minutes** | ⭐ **Paced**. Shatters standard stone in 1 hit. |
| **5. Advanced Bag** | Reinforced Hauler (Cap 100) | 500 | **4–5 trips** | **2 trips** | **~6 minutes** | ⭐ **Paced**. Prepares player for deep cavern runs. |
| **6. Stage 3 Bulkhead** | Bulkhead Gate Unlock | 5,000 | 40 trips (Stage 1) | **2.5 trips in Stage 2** | **~8–10 minutes** | ⭐ **Gate Well Positioned**. Directs player to Stage 2. |

### C. Does the 250 Coin Egg Compete Unfairly with Equipment?

**Analysis**:
- If a player chooses to hatch an egg before buying the Tier 2 Pickaxe, they spend 250 Coins to gain Scrap Kitty or Iron Mole (+2 or +3 DMG).
- Because Starter Pickaxe deals 10 DMG, the 2 DMG assist provides an extra ~10% damage.
- Conversely, spending 100 Coins on the Reinforced Iron Pickaxe provides **+100% damage** (doubling DPS from 20 to 40).
- **Conclusion**: The egg does not break early progression or invalidate pickaxe upgrades. It acts as an engaging side-grade / cosmetic milestone. The economy naturally rewards players who follow the optimal path (Pickaxe \(\to\) Backpack \(\to\) Egg) while remaining accessible enough (2 trips) for pet-focused players without trapping them.

---

## 4. Security & Server Boundary Review

The following 7 server security edge cases were tested in Play mode:

| Security Test Case | Target System | Tested Attack / Exploitation | Server Response | Result |
| :--- | :--- | :--- | :--- | :---: |
| **1. Fake Node Mining** | `MiningService` | Requested damage on `"FakeNode_999"` | `NODE_NOT_FOUND` | ✅ **Rejected** |
| **2. Reach Exploitation** | `MiningService` | Attempted swing while 500 studs away | `TOO_FAR` / `COOLDOWN_ACTIVE` | ✅ **Rejected** |
| **3. Remote Ore Selling** | `PlotService` | Attempted `SellBackpack` while away from pad | `TOO_FAR_FROM_STATION` | ✅ **Rejected** |
| **4. Remote Egg Hatching** | `PetService` | Attempted `HatchEgg` while 500 studs away | `TOO_FAR_FROM_STATION` | ✅ **Rejected** |
| **5. Unfunded Hatch** | `PetService` | Attempted `HatchEgg` with 0 Coins at incubator | `INSUFFICIENT_FUNDS` | ✅ **Rejected** |
| **6. Tier Skipping** | `EquipmentService` | Attempted to jump from Pickaxe Tier 1 to Tier 3 | Server forces `currentLevel + 1` sequentially | ✅ **Rejected** |
| **7. Unfunded Equipment** | `EquipmentService` | Attempted upgrade request with 0 Coins | `INSUFFICIENT_FUNDS` / `INVALID_TARGET` | ✅ **Rejected** |

All core gameplay mutations remain strictly server-authoritative.

---

## 5. Concrete Observations & Recommendations

### Observation 1: Quantized Pet Cadence
- **Symptom**: Scrap Kitty has `MiningSpeed = 0.8s`, but because `MiningService:ProcessMineRequest` only evaluates assists when the player manually swings (minimum 0.5s intervals), Scrap Kitty only triggers on swings at 0.0s, 1.0s, 2.0s. It effectively acts identical to Rusty Pup (1.0s).
- **Impact**: Players hatching Scrap Kitty for its "Rapid Striker" feature do not experience faster strike cadence during continuous rapid swinging.
- **Recommended Minimal Polish (Future Task)**:
  - Option A: Allow pet assists to run on an autonomous background heartbeat loop in `PetService` while the owner is actively targeting/mining a node, rather than binding pet strikes strictly to manual swing timestamps.
  - Option B: Slightly adjust pet assist damage or swing speed parameters so Scrap Kitty deals 2 DMG every 0.8s independently of manual click rate.

### Observation 2: Stage 1 Breakpoint Overshoot on Round HP Nodes
- **Symptom**: Because Stone (30), Copper (60), and Coal (90) have HP exactly divisible by 10, a Starter Pickaxe (10 Power) leaves 8, 4, and 2 HP on the penultimate hit, requiring the same number of hits with or without a 2 DMG pet assist.
- **Impact**: Novice players with Starter Pickaxe do not feel an immediate reduction in swing count on Stage 1 nodes when equipped with Rusty Pup.
- **Recommended Minimal Polish (Future Task)**:
  - Adjusting Coal from 90 HP to 85 HP or 80 HP would allow Rusty Pup and Scrap Kitty to break Coal in **7 or 8 hits instead of 9 hits**, immediately showcasing companion utility to new players.
