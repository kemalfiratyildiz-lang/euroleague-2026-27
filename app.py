import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from pathlib import Path

st.set_page_config(
    page_title="EuroLeague Net Rating Dashboard",
    layout="wide"
)

def clean_number(x):
    if pd.isna(x):
        return None
    x = str(x).strip().replace(",", ".")
    x = re.sub(r"[^0-9.\\-]", "", x)
    return pd.to_numeric(x, errors="coerce")


df = pd.read_csv(Path(__file__).with_name("euroleague_merged_dashboard_data.csv"))
df.columns = df.columns.str.strip()

df["Player"] = df["Player"].astype(str).str.strip()
df["Team"] = df["Team"].astype(str).str.strip()

df.loc[df["Team"] == "LYV", "Team"] = "ASV"

off_col = "ORtg"
def_col = "DRtg"

possible_games = ["GP", "Games", "Game", "G", "Matches"]
possible_minutes = ["MPG", "MIN", "Minutes", "Min", "MP"]

game_col = next((c for c in possible_games if c in df.columns), None)
minute_col = next((c for c in possible_minutes if c in df.columns), None)

if game_col is None:
    st.error("Maç sayısı kolonu bulunamadı.")
    st.stop()
if minute_col is None:
    st.error("Dakika kolonu bulunamadı.")
    st.write(list(df.columns))
    st.stop()

for c in [off_col, def_col, game_col, minute_col]:
    df[c] = df[c].apply(clean_number)

df["Net Rating"] = df[off_col] - df[def_col]

df = df.dropna(
    subset=[
        "Player",
        "Team",
        off_col,
        def_col,
        minute_col,
        game_col,
        "Net Rating"
    ]
)

df[off_col] = df[off_col].round(1)
df[def_col] = df[def_col].round(1)
df["Net Rating"] = df["Net Rating"].round(1)
df[minute_col] = df[minute_col].round(1)
df[game_col] = df[game_col].round(0)

base_filtered = df.copy()

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(37,99,235,0.45) 0%, transparent 22%),
        radial-gradient(circle at 85% 10%, rgba(168,85,247,0.28) 0%, transparent 18%),
        radial-gradient(circle at 50% 85%, rgba(14,165,233,0.20) 0%, transparent 25%),
        linear-gradient(180deg, #020617 0%, #030b1a 30%, #02040a 100%);
    color: white;
    background-attachment: fixed;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,28,56,0.98), rgba(10,19,40,0.98));
    border-right: 1px solid rgba(59,130,246,0.18);
    box-shadow: 0 0 30px rgba(37,99,235,0.12);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

h1, h2, h3, h4, p, label, span, div {
    color: white;
    font-family: Arial, Helvetica, sans-serif;
}

.main-title {
    font-size: 46px;
    font-weight: 900;
    margin-bottom: 0px;
    letter-spacing: -1.6px;
    background: linear-gradient(90deg, #ffffff 0%, #dbeafe 45%, #93c5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-title {
    color: #9fb4d9 !important;
    font-size: 17px;
    margin-bottom: 30px;
}

.card {
    background: linear-gradient(145deg, rgba(17,24,39,0.88), rgba(15,23,42,0.92));
    border: 1px solid rgba(59,130,246,0.20);
    border-radius: 24px;
    padding: 26px;
    text-align: center;
    backdrop-filter: blur(10px);
    box-shadow:
        0 0 30px rgba(37,99,235,0.14),
        0 0 80px rgba(59,130,246,0.06),
        inset 0 1px 0 rgba(255,255,255,0.04);
}

.card-title {
    color: #93a8c7 !important;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 10px;
}

.card-value {
    font-size: 38px;
    font-weight: 900;
}

.good {
    color: #22c55e !important;
    text-shadow: 0 0 14px rgba(34,197,94,0.45);
}

.bad {
    color: #ef4444 !important;
    text-shadow: 0 0 14px rgba(239,68,68,0.45);
}

[data-testid="stDataFrame"] {
    background: rgba(17,24,39,0.92);
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(59,130,246,0.12);
}

.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    background: rgba(17,24,39,0.92);
    border-radius: 14px;
    border: 1px solid rgba(59,130,246,0.14);
}

.js-plotly-plot {
    border-radius: 24px;
    overflow: hidden;
}

[data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(17,24,39,0.92), rgba(15,23,42,0.94));
    border-radius: 18px;
    border: 1px solid rgba(59,130,246,0.16);
    padding: 14px;
    box-shadow: 0 0 24px rgba(37,99,235,0.10);
}

</style>
""", unsafe_allow_html=True)

st.sidebar.title("EuroLeague Filters")

teams = ["All"] + sorted(df["Team"].dropna().unique())
selected_team = st.sidebar.selectbox("Team", teams)

if selected_team == "All":
    filtered = base_filtered.copy()
    sidebar_note = "Minimum maç ve dakika filtresi yok"
else:
    filtered = df[df["Team"] == selected_team].copy()
    sidebar_note = "Team selected: all players shown"

players = ["All"] + sorted(filtered["Player"].dropna().unique())
selected_player = st.sidebar.selectbox("Find Player", players)

st.sidebar.markdown("---")
st.sidebar.caption(sidebar_note)
st.sidebar.caption("Net Rating = ORtg - DRtg")

st.markdown(
    '<div class="main-title">EuroLeague 2026–27 Net Rating Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">İlk 4 hafta • 263 oyuncu • RealGM bireysel ORtg − DRtg</div>',
    unsafe_allow_html=True
)

team_games = df.groupby("TeamName")[game_col].max()
with st.expander("Veri kapsamı ve yöntem"):
    st.write("Kaynak: Kullanıcının RealGM’den kopyaladığı Advanced Stats ve Averages sekmeleri. Oyuncu ve takım bağlantılarındaki kimliklerle eşleştirildi. Minimum maç/dakika filtresi uygulanmadı. Net Rating = ORtg − DRtg; gösterilen bir ondalıklı kaynak değerleri kullanılır.")
    st.dataframe(team_games.rename("Dosyada en yüksek oyuncu maç sayısı").reset_index(), hide_index=True)

if filtered.empty:
    st.error("Filtre sonrası oyuncu kalmadı.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)

avg_ortg = filtered[off_col].mean()
avg_drtg = filtered[def_col].mean()
avg_net = filtered["Net Rating"].mean()
player_count = filtered["Player"].nunique()

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Avg ORtg</div>
        <div class="card-value">{avg_ortg:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Avg DRtg</div>
        <div class="card-value">{avg_drtg:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    cls = "good" if avg_net >= 0 else "bad"
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Avg Net Rating</div>
        <div class="card-value {cls}">{avg_net:+.1f}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Players</div>
        <div class="card-value">{player_count}</div>
    </div>
    """, unsafe_allow_html=True)

if selected_player != "All":
    p = filtered[filtered["Player"] == selected_player].iloc[0]

    st.subheader(f"{selected_player} — Player Impact Card")

    p1, p2, p3, p4 = st.columns(4)

    p1.metric("ORtg", f"{p[off_col]:.1f}")
    p2.metric("DRtg", f"{p[def_col]:.1f}")
    p3.metric("Net Rating", f"{p['Net Rating']:+.1f}")
    p4.metric("Minutes", f"{p[minute_col]:.1f}")

st.subheader("Offensive Rating vs Defensive Rating")

fig = px.scatter(
    filtered,
    x=off_col,
    y=def_col,
    color="Team",
    size=minute_col,
    text="Player",
    hover_name="Player",
    custom_data=["Team", "Net Rating", minute_col, game_col],
    size_max=44,
)

fig.update_traces(
    textposition="top center",
    textfont=dict(size=10, color="white"),
    marker=dict(line=dict(width=1, color="rgba(255,255,255,0.35)")),
    hovertemplate=
    "<b>%{hovertext}</b><br>" +
    "Team: %{customdata[0]}<br>" +
    "ORtg: %{x:.1f}<br>" +
    "DRtg: %{y:.1f}<br>" +
    "Net Rating: %{customdata[1]:+.1f}<br>" +
    "Minutes: %{customdata[2]:.1f}<br>" +
    "Games: %{customdata[3]:.0f}<extra></extra>"
)

fig.add_vline(
    x=filtered[off_col].mean(),
    line_dash="dash",
    line_color="rgba(255,255,255,0.7)"
)

fig.add_hline(
    y=filtered[def_col].mean(),
    line_dash="dash",
    line_color="rgba(255,255,255,0.7)"
)

if selected_player != "All":
    hp = filtered[filtered["Player"] == selected_player]

    fig.add_trace(
        go.Scatter(
            x=hp[off_col],
            y=hp[def_col],
            mode="markers",
            marker=dict(
                size=60,
                color="rgba(0,0,0,0.92)",
                line=dict(width=0)
            ),
            hoverinfo="skip",
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=hp[off_col],
            y=hp[def_col],
            mode="markers",
            marker=dict(
                size=50,
                color="rgba(250,204,21,0.28)",
                line=dict(width=6, color="#facc15")
            ),
            hoverinfo="skip",
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=hp[off_col],
            y=hp[def_col],
            mode="markers+text",
            text=hp["Player"],
            textposition="top center",
            customdata=hp[["Team", "Net Rating", minute_col, game_col]],
            marker=dict(
                size=28,
                symbol="star",
                color="#facc15",
                line=dict(width=3, color="white")
            ),
            name=f"Selected: {selected_player}",
            hovertemplate=
            "<b>%{text}</b><br>" +
            "Team: %{customdata[0]}<br>" +
            "ORtg: %{x:.1f}<br>" +
            "DRtg: %{y:.1f}<br>" +
            "Net Rating: %{customdata[1]:+.1f}<br>" +
            "Minutes: %{customdata[2]:.1f}<br>" +
            "Games: %{customdata[3]:.0f}<extra></extra>"
        )
    )

fig.update_yaxes(
    autorange="reversed",
    title="DRtg — lower is better",
    gridcolor="rgba(255,255,255,0.10)",
    zerolinecolor="rgba(255,255,255,0.15)"
)

fig.update_xaxes(
    title="ORtg — higher is better",
    gridcolor="rgba(255,255,255,0.10)",
    zerolinecolor="rgba(255,255,255,0.15)"
)

fig.update_layout(
    height=780,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,23,42,0.72)",
    font=dict(color="white", size=13),
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
)

st.plotly_chart(fig, use_container_width=True)

st.caption("Sağ üst bölge en değerli alan: yüksek ORtg + düşük DRtg.")
st.caption("Bu değerler RealGM bireysel rating tahminleridir; sahadayken takım net rating’i veya on/off değildir.")

st.subheader("Multi Player Comparison")

compare_players = st.multiselect(
    "Karşılaştırmak istediğin oyuncuları seç",
    sorted(filtered["Player"].unique()),
    default=sorted(filtered["Player"].unique())[:3],
    max_selections=8
)

if compare_players:
    player_compare = (
        filtered[filtered["Player"].isin(compare_players)]
        [["Player", "Team", off_col, def_col, "Net Rating", minute_col, game_col]]
        .sort_values("Net Rating", ascending=False)
        .reset_index(drop=True)
    )

    st.dataframe(player_compare, use_container_width=True, hide_index=True)

    tab1, tab2 = st.tabs(["Sadece Seçilen Oyuncular", "Tüm Oyuncular İçinde Vurgula"])

    with tab1:
        fig_selected_players = px.scatter(
            player_compare,
            x=off_col,
            y=def_col,
            color="Team",
            size=minute_col,
            text="Player",
            hover_name="Player",
            custom_data=["Team", "Net Rating", minute_col, game_col],
            size_max=55,
            title="Selected Players Only"
        )

        fig_selected_players.update_traces(
            textposition="top center",
            textfont=dict(size=12, color="white"),
            marker=dict(line=dict(width=2, color="white")),
            hovertemplate=
            "<b>%{hovertext}</b><br>" +
            "Team: %{customdata[0]}<br>" +
            "ORtg: %{x:.1f}<br>" +
            "DRtg: %{y:.1f}<br>" +
            "Net Rating: %{customdata[1]:+.1f}<br>" +
            "Minutes: %{customdata[2]:.1f}<br>" +
            "Games: %{customdata[3]:.0f}<extra></extra>"
        )

        fig_selected_players.update_yaxes(
            autorange="reversed",
            title="DRtg — lower is better",
            gridcolor="rgba(255,255,255,0.10)"
        )

        fig_selected_players.update_xaxes(
            title="ORtg — higher is better",
            gridcolor="rgba(255,255,255,0.10)"
        )

        fig_selected_players.update_layout(
            height=520,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.72)",
            font=dict(color="white"),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )

        st.plotly_chart(fig_selected_players, use_container_width=True)

    with tab2:
        fig_highlight_players = go.Figure()

        fig_highlight_players.add_trace(
            go.Scatter(
                x=filtered[off_col],
                y=filtered[def_col],
                mode="markers",
                customdata=filtered[["Team", "Net Rating", minute_col, game_col]],
                marker=dict(
                    size=10,
                    color="rgba(148,163,184,0.25)",
                    line=dict(width=0)
                ),
                text=filtered["Player"],
                name="All Players",
                hovertemplate=
                "<b>%{text}</b><br>" +
                "Team: %{customdata[0]}<br>" +
                "ORtg: %{x:.1f}<br>" +
                "DRtg: %{y:.1f}<br>" +
                "Net Rating: %{customdata[1]:+.1f}<br>" +
                "Minutes: %{customdata[2]:.1f}<br>" +
                "Games: %{customdata[3]:.0f}<extra></extra>"
            )
        )

        fig_highlight_players.add_trace(
            go.Scatter(
                x=player_compare[off_col],
                y=player_compare[def_col],
                mode="markers+text",
                text=player_compare["Player"],
                textposition="top center",
                customdata=player_compare[["Team", "Net Rating", minute_col, game_col]],
                marker=dict(
                    size=28,
                    symbol="star",
                    color="#facc15",
                    line=dict(width=3, color="white")
                ),
                name="Selected Players",
                hovertemplate=
                "<b>%{text}</b><br>" +
                "Team: %{customdata[0]}<br>" +
                "ORtg: %{x:.1f}<br>" +
                "DRtg: %{y:.1f}<br>" +
                "Net Rating: %{customdata[1]:+.1f}<br>" +
                "Minutes: %{customdata[2]:.1f}<br>" +
                "Games: %{customdata[3]:.0f}<extra></extra>"
            )
        )

        fig_highlight_players.update_yaxes(
            autorange="reversed",
            title="DRtg — lower is better",
            gridcolor="rgba(255,255,255,0.10)"
        )

        fig_highlight_players.update_xaxes(
            title="ORtg — higher is better",
            gridcolor="rgba(255,255,255,0.10)"
        )

        fig_highlight_players.update_layout(
            height=560,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.72)",
            font=dict(color="white"),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )

        st.plotly_chart(fig_highlight_players, use_container_width=True)

st.subheader("Team Comparison — Oyuncu Rating Ortalamaları")
st.caption("Oyuncuların eşit ağırlıklı ortalaması; takımın kendi net rating değeri değildir.")

team_summary = (
    base_filtered.groupby("Team", as_index=False)
    .agg(
        Players=("Player", "nunique"),
        Avg_ORtg=(off_col, "mean"),
        Avg_DRtg=(def_col, "mean"),
        Avg_Net_Rating=("Net Rating", "mean"),
        Avg_Minutes=(minute_col, "mean")
    )
    .sort_values("Avg_Net_Rating", ascending=False)
)

team_summary["Avg_ORtg"] = team_summary["Avg_ORtg"].round(1)
team_summary["Avg_DRtg"] = team_summary["Avg_DRtg"].round(1)
team_summary["Avg_Net_Rating"] = team_summary["Avg_Net_Rating"].round(1)
team_summary["Avg_Minutes"] = team_summary["Avg_Minutes"].round(1)

selected_teams_compare = st.multiselect(
    "Karşılaştırmak istediğin takımları seç",
    sorted(team_summary["Team"].unique()),
    default=team_summary.head(5)["Team"].tolist(),
    max_selections=10
)

if selected_teams_compare:
    team_compare = team_summary[
        team_summary["Team"].isin(selected_teams_compare)
    ].copy()

    st.dataframe(team_compare, use_container_width=True, hide_index=True)

    tab3, tab4 = st.tabs(["Sadece Seçilen Takımlar", "Tüm Oyuncular İçinde Vurgula"])

    with tab3:
        fig_team_bar = px.bar(
            team_compare.sort_values("Avg_Net_Rating", ascending=False),
            x="Team",
            y="Avg_Net_Rating",
            text_auto=".1f",
            title="Selected Teams — Avg Net Rating"
        )

        fig_team_bar.update_layout(
            height=480,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.72)",
            font=dict(color="white")
        )

        st.plotly_chart(fig_team_bar, use_container_width=True)

    with tab4:
        highlighted_team_players = base_filtered[
            base_filtered["Team"].isin(selected_teams_compare)
        ]

        fig_team_highlight = go.Figure()

        fig_team_highlight.add_trace(
            go.Scatter(
                x=base_filtered[off_col],
                y=base_filtered[def_col],
                mode="markers",
                customdata=base_filtered[["Team", "Net Rating", minute_col, game_col]],
                marker=dict(
                    size=10,
                    color="rgba(148,163,184,0.22)",
                    line=dict(width=0)
                ),
                text=base_filtered["Player"],
                name="All Players",
                hovertemplate=
                "<b>%{text}</b><br>" +
                "Team: %{customdata[0]}<br>" +
                "ORtg: %{x:.1f}<br>" +
                "DRtg: %{y:.1f}<br>" +
                "Net Rating: %{customdata[1]:+.1f}<br>" +
                "Minutes: %{customdata[2]:.1f}<br>" +
                "Games: %{customdata[3]:.0f}<extra></extra>"
            )
        )

        fig_team_highlight.add_trace(
            go.Scatter(
                x=highlighted_team_players[off_col],
                y=highlighted_team_players[def_col],
                mode="markers+text",
                text=highlighted_team_players["Player"],
                textposition="top center",
                customdata=highlighted_team_players[["Team", "Net Rating", minute_col, game_col]],
                marker=dict(
                    size=18,
                    symbol="star",
                    color="#38bdf8",
                    line=dict(width=2, color="white")
                ),
                name="Selected Team Players",
                hovertemplate=
                "<b>%{text}</b><br>" +
                "Team: %{customdata[0]}<br>" +
                "ORtg: %{x:.1f}<br>" +
                "DRtg: %{y:.1f}<br>" +
                "Net Rating: %{customdata[1]:+.1f}<br>" +
                "Minutes: %{customdata[2]:.1f}<br>" +
                "Games: %{customdata[3]:.0f}<extra></extra>"
            )
        )

        fig_team_highlight.update_yaxes(
            autorange="reversed",
            title="DRtg — lower is better",
            gridcolor="rgba(255,255,255,0.10)"
        )

        fig_team_highlight.update_xaxes(
            title="ORtg — higher is better",
            gridcolor="rgba(255,255,255,0.10)"
        )

        fig_team_highlight.update_layout(
            height=620,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.72)",
            font=dict(color="white"),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )

        st.plotly_chart(fig_team_highlight, use_container_width=True)

st.subheader("Net Rating Leaderboard")

leaderboard = (
    filtered[
        [
            "Player",
            "Team",
            off_col,
            def_col,
            "Net Rating",
            minute_col,
            game_col
        ]
    ]
    .sort_values("Net Rating", ascending=False)
    .reset_index(drop=True)
)

st.dataframe(
    leaderboard,
    use_container_width=True,
    hide_index=True
)