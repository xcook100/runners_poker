## streamlit run runners_poker_v01.py

import streamlit as st
import pandas as pd

# -----------------------------
# Config
# -----------------------------
st.set_page_config(page_title="Runners Poker v0.1", page_icon="🎴")

st.title("🎴 Runners Poker v0.1")
st.caption("Win Chips → Sit back and realx."
           " Lose Chips → Time to run. 😈")

# === Rules Expander ===
with st.expander("📘 How Runners Poker Works"):
    st.markdown(
        """
### 🎴 Quick Rules

- Everyone starts with the **same number of chips**.  
- You play **normal poker** — no rule changes.  
- At the end, each player enters their **final chip stack**.  
- The app converts chips into **kilometres of running**.  

### 🧮 Equal Mode

- Everyone shares the same **Max KM**.  
- If you end with **more than your starting chips** → **0 km**  
- If you end with **0 chips** → **full max distance**  
- Everyone’s punishment scales equally based on chip percentage.

### 🏃 Weighted Mode

Your fitness category applies a multiplier on top of Equal Mode:

- **Couch Potato** → ×0.6  
- **Beginner** → ×0.8  
- **Casual** → ×1.0  
- **Regular** → ×1.2  
- **Athlete** → ×1.4  

Weighted punishment = `Base KM × Multiplier`.

### 🛠 Custom Mode

- Each player sets **their own Max KM** (their personal ceiling).  
- The punishment scales as a percentage of **that player’s** max.  
- Great for mixed-ability groups who want things to feel fair.

### 😈 Core Concept

**Win Chips → no run.  
Lose Chips → time to run.**
        """
    )

st.markdown("### 1. Game Setup")

# 1) Choose mode first
mode = st.radio(
    "Select mode",
    [
        "Equal (everyone same punishment)",
        "Weighted (based on fitness category)",
        "Custom (each player sets their own max distance)",
    ],
    index=0
)

mode_equal = mode.startswith("Equal")
mode_weighted = mode.startswith("Weighted")
mode_custom = mode.startswith("Custom")

# Forfeit type (one per game)
forfeit_type = st.selectbox(
    "Forfeit type",
    [
        "Run (km)",
        "Cycle (km)",
        "Burpees (reps)",
        "Steps (x1000)",
    ],
    index=0,
    help="What kind of punishment is this game using?"
)

# How to describe the units and action in the summary
FORFEIT_TYPE_CONFIG = {
    "Run (km)": {"unit": "km", "activity": "run"},
    "Cycle (km)": {"unit": "km", "activity": "cycle"},
    "Burpees (reps)": {"unit": "burpees", "activity": None},
    "Steps (x1000)": {"unit": "k steps", "activity": None},
}

# 2) Starting chips (always needed)
col1, col2 = st.columns(2)
with col1:
    starting_chips_input = st.number_input(
        "Starting chips per player",
        min_value=1,
        value=1000,
        step=100
    )
    starting_chips = int(starting_chips_input)

# 3) Max distance only for Equal + Weighted
with col2:
    if mode_equal or mode_weighted:
        cfg_forfeit = FORFEIT_TYPE_CONFIG.get(
            forfeit_type,
            {"unit": "units", "activity": None}
        )
        unit_label = cfg_forfeit["unit"]

        max_km = st.number_input(
            f"Max forfeit ({unit_label})",
            min_value=0.1,
            value=10.0,
            step=0.5,
            format="%.1f"
        )
    else:
        max_km = None
        st.info("Custom Mode: each player will set their own max punishment in the next step.")

num_players_input = st.number_input(
    "Number of players",
    min_value=2,
    max_value=10,
    value=4,
    step=1
)
num_players = int(num_players_input)

# Pick the deadline date
completion_date = st.date_input(
    "Select the deadline for completing the forfeits",
    help="Players must finish their punishment(s) by this date."
)

st.markdown("---")
st.markdown("### 2. Players & Settings")

# Fitness categories & multipliers
fitness_categories = ["Couch Potato", "Beginner", "Casual", "Regular", "Athlete"]
multipliers = {
    "Couch Potato": 0.6,
    "Beginner": 0.8,
    "Casual": 1.0,
    "Regular": 1.2,
    "Athlete": 1.4,
}

players = []

for i in range(num_players):
    st.markdown(f"**Player {i+1}**")
    c1, c2 = st.columns(2)

    with c1:
        name = st.text_input(
            f"Name for Player {i+1}",
            value=f"Player {i+1}",
            key=f"name_{i}"
        )

    player_data = {"name": name}

    if mode_weighted:
        with c2:
            category = st.selectbox(
                f"Fitness category for {name}",
                options=fitness_categories,
                index=2,  # default "Casual"
                key=f"cat_{i}"
            )
        player_data["fitness"] = category

    elif mode_custom:
        with c2:
            cfg_forfeit = FORFEIT_TYPE_CONFIG.get(
                forfeit_type,
                {"unit": "units", "activity": None}
            )
            unit_label = cfg_forfeit["unit"]

            max_km_player = st.number_input(
                f"Max forfeit for {name} ({unit_label})",
                min_value=0.1,
                value=10.0,
                step=0.5,
                key=f"maxkm_{i}"
            )
        player_data["max_km"] = max_km_player

    players.append(player_data)

st.markdown("---")
st.markdown("### 3. Final Chip Counts")

st.write("After you finish playing poker normally, enter each player’s final chip stack below:")

total_final_chips = 0
for p in players:
    p["chips"] = st.number_input(
        f"{p['name']} – final chips",
        min_value=0,
        value=0,
        step=int(starting_chips / 10) if starting_chips >= 10 else 1,
        key=f"chips_{p['name']}"
    )
    total_final_chips += p["chips"]

# Calculate expected total starting chips
total_starting_chips = starting_chips * num_players

if st.button("Calculate forfeits 🚀"):
    # Non-blocking sanity check for chip total
    if total_final_chips != total_starting_chips:
        diff = total_final_chips - total_starting_chips
        if diff > 0:
            st.warning(
                f"Chip check: Final total chips ({total_final_chips}) are "
                f"**more** than starting total ({total_starting_chips}). "
                "No big deal, but you might have miscounted or added extra chips."
            )
        else:
            st.warning(
                f"Chip check: Final total chips ({total_final_chips}) are "
                f"**less** than starting total ({total_starting_chips}). "
                "Maybe a chip went missing or got miscounted. "
                "We’ll still calculate forfeits as normal. 💸🎴"
            )

    # Configure unit labels for the table + summary
    cfg = FORFEIT_TYPE_CONFIG.get(forfeit_type, {"unit": "units", "activity": None})
    unit = cfg["unit"]
    activity = cfg["activity"]
    forfeit_col_name = f"Forfeit ({unit})"
    player_max_col_name = f"Player max ({unit})"

    # Compute forfeits
    rows = []
    for p in players:
        chips = p["chips"]

        # Chip ratio
        chip_ratio = min(chips / starting_chips, 1) if starting_chips > 0 else 0

        # Equal / base km using global max_km (for equal + weighted)
        if mode_equal or mode_weighted:
            base_km_equal = 0.0 if chips >= starting_chips else max_km * (1 - chip_ratio)
        else:
            base_km_equal = None

        # Weighted km (if applicable)
        if mode_weighted:
            mult = multipliers.get(p.get("fitness", "Casual"), 1.0)
            forfeit_km = base_km_equal * mult

        # Custom km (per-player max)
        elif mode_custom:
            player_max = p.get("max_km", 10.0)
            base_km_custom = 0.0 if chips >= starting_chips else player_max * (1 - chip_ratio)
            forfeit_km = base_km_custom

        # Equal mode
        else:  # mode_equal
            forfeit_km = base_km_equal

        # Build row depending on mode
        if mode_weighted:
            rows.append(
                {
                    "Player": p["name"],
                    "Fitness category": p.get("fitness", "-"),
                    "Final chips": chips,
                    "Chip % of start": round(chip_ratio * 100, 1),
                    forfeit_col_name: (int(round(forfeit_km, 2)) if float(round(forfeit_km, 2)).is_integer() else round(forfeit_km, 2)),
                }
            )
        elif mode_custom:
            rows.append(
                {
                    "Player": p["name"],
                    player_max_col_name: (int(round(p.get("max_km", 10.0), 2)) if float(round(p.get("max_km", 10.0), 2)).is_integer() else round(p.get("max_km", 10.0), 2)),
                    "Final chips": chips,
                    "Chip % of start": round(chip_ratio * 100, 1),
                    forfeit_col_name: (int(round(forfeit_km, 2)) if float(round(forfeit_km, 2)).is_integer() else round(forfeit_km, 2)),
                }
            )
        else:  # Equal
            rows.append(
                {
                    "Player": p["name"],
                    "Final chips": chips,
                    "Chip % of start": round(chip_ratio * 100, 1),
                    forfeit_col_name: (int(round(forfeit_km, 2)) if float(round(forfeit_km, 2)).is_integer() else round(forfeit_km, 2)),
                }
            )

    df = pd.DataFrame(rows)

    st.markdown("### 4. Forfeit Results")
    st.dataframe(df, width="stretch")

    st.markdown("#### Summary")

    for r in rows:
        amount = r[forfeit_col_name]
        if amount == 0:
            if activity:
                st.write(
                    f"**{r['Player']}** → 🎉 **No {activity} required!** (0 {unit})"
                )
            else:
                st.write(
                    f"**{r['Player']}** → 🎉 **No {unit} required!** (0 {unit})"
                )
        else:
            if activity:
                st.write(
                    f"**{r['Player']}** → {amount} {unit} to {activity} "
                    f"by **{completion_date.strftime('%d %b %Y')}**."
                )
            else:
                st.write(
                    f"**{r['Player']}** → {amount} {unit} "
                    f"by **{completion_date.strftime('%d %b %Y')}**."
                )

    # New game / reset button
    if st.button("🔄 New game / reset"):
        # Rerun the app to clear all inputs and start fresh
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()

    st.markdown("---")

else:
    st.caption("👆 Enter final chips, then hit **Calculate forfeits** to see who’s running how far.")