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

- **Non-runner** → ×0.6  
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
        max_km = st.number_input(
            "Max forfeit distance (km)",
            min_value=0.1,
            value=10.0,
            step=0.5,
            format="%.1f"
        )
    else:
        max_km = None
        st.info("Custom Mode: each player will set their own max distance in the next step.")

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
    help="Players must finish their punishment run(s) by this date."
)

st.markdown("---")
st.markdown("### 2. Players & Settings")

# Fitness categories & multipliers
fitness_categories = ["Non-runner", "Beginner", "Casual", "Regular", "Athlete"]
multipliers = {
    "Non-runner": 0.6,
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
            max_km_player = st.number_input(
                f"Max distance for {name} (km)",
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
                    "Forfeit (km)": round(forfeit_km, 2),
                }
            )
        elif mode_custom:
            rows.append(
                {
                    "Player": p["name"],
                    "Player max km": round(p.get("max_km", 10.0), 2),
                    "Final chips": chips,
                    "Chip % of start": round(chip_ratio * 100, 1),
                    "Forfeit (km)": round(forfeit_km, 2),
                }
            )
        else:  # Equal
            rows.append(
                {
                    "Player": p["name"],
                    "Final chips": chips,
                    "Chip % of start": round(chip_ratio * 100, 1),
                    "Forfeit (km)": round(forfeit_km, 2),
                }
            )

    df = pd.DataFrame(rows)

    st.markdown("### 4. Forfeit Results")
    st.dataframe(df, width="stretch")

    st.markdown("#### Summary")
    for r in rows:
        km = r["Forfeit (km)"]
        if km == 0:
            st.write(
                f"**{r['Player']}** → 🎉 **No run required!** (0 km)"
            )
        else:
            st.write(
                f"**{r['Player']}** → {km} km to run "
                f"by **{completion_date.strftime('%d %b %Y')}**."
            )

    st.markdown("---")

else:
    st.caption("👆 Enter final chips, then hit **Calculate forfeits** to see who’s running how far.")