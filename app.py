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
.stApp {background:#101629;color:#f6f7fb;}
[data-testid="stHeader"] {background:rgba(16,22,41,.92);}
[data-testid="stSidebar"] {background:#151d34;border-right:1px solid #2b3550;}
[data-testid="stSidebar"] h1 {font-size:24px;}
h1,h2,h3,p,label {color:#f6f7fb;}
h1,h2,h3,.main-title {font-family:Arial,Helvetica,sans-serif;}
.block-container {max-width:1500px;padding-top:2.5rem;}
.main-title {font-size:clamp(30px,4.5vw,58px);font-weight:900;letter-spacing:-2px;line-height:1.05;color:#f6f7fb;}
.eyebrow {color:#f1d75c;font-size:12px;font-weight:800;letter-spacing:3px;margin-bottom:14px;}
.sub-title {color:#a6b1cb;font-size:15px;padding:18px 0 24px;border-bottom:2px solid #f1d75c;margin-bottom:26px;}
.card {background:#19213a;border:1px solid #303a55;border-radius:12px;padding:22px 20px;text-align:left;}
.card-title {color:#a6b1cb;font-size:11px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:10px;}
.card-value {font-size:36px;font-weight:800;color:#f6f7fb;font-variant-numeric:tabular-nums;}
.good {color:#73dab0;}.bad {color:#ff8e97;}
[data-testid="stMetric"] {background:#19213a;border:1px solid #303a55;padding:18px;border-radius:12px;}
[data-testid="stDataFrame"] {border:1px solid #303a55;border-radius:10px;overflow:hidden;}
.stSelectbox div[data-baseweb="select"],.stMultiSelect div[data-baseweb="select"] {background:#19213a;color:#f6f7fb;}
.js-plotly-plot {border-radius:12px;overflow:hidden;}
[data-testid="stCaptionContainer"] {color:#a6b1cb;}
[data-baseweb="tab"] {color:#a6b1cb;}
[data-baseweb="tab"][aria-selected="true"] {color:#f1d75c;}
@media(max-width:640px) {.card {padding:14px 10px;}.card-value {font-size:26px;}.main-title {letter-spacing:-1px;}}
</style>
""", unsafe_allow_html=True)

# A consistent palette across filters and comparison charts.
TEAM_COLORS = dict(zip(sorted(df["Team"].unique()),
    ["#f1d75c", "#73dab0", "#87b9ff", "#ff8e97", "#c1a2ff",
     "#ffb76b", "#6bdddf", "#ec9fd4", "#a9cf78", "#b7c6e5",
     "#d3b17b", "#81a6dd", "#b1e5c5", "#dc8cbd", "#e9e29d",
     "#bcaff0", "#ffa898", "#88c8b7", "#c4cce0", "#c0bd77"]))
px.defaults.color_discrete_map = TEAM_COLORS
px.defaults.template = "plotly_dark"

st.sidebar.title("EUROLEAGUE")
min_minutes = st.sidebar.slider("Minimum dakika ortalaması", 0.0, 40.0, 0.0, 0.5, format="%.1f dk")
base_filtered = df[df[minute_col] >= min_minutes].copy()

teams = ["All"] + sorted(df["Team"].dropna().unique())
selected_team = st.sidebar.selectbox("Takım", teams)

if selected_team == "All":
    filtered = base_filtered.copy()

else:
    filtered = base_filtered[base_filtered["Team"] == selected_team].copy()

players = ["All"] + sorted(filtered["Player"].dropna().unique())
selected_player = st.sidebar.selectbox("Oyuncu bul", players)

st.sidebar.markdown("---")
st.sidebar.caption(f"{len(filtered)} oyuncu · En az {min_minutes:g} dk")

st.markdown(
    '<div class="eyebrow">EUROLEAGUE / 2026–27 / İLK 4 HAFTA</div><div class="main-title">PLAYER EFFICIENCY<br>LANDSCAPE</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="sub-title">{len(filtered)} oyuncu · {filtered["Team"].nunique()} takım · İlk 4 hafta</div>',
    unsafe_allow_html=True
)

if filtered.empty:
    st.info("Bu dakika sınırına uyan oyuncu yok. Soldaki süreyi azaltabilirsin.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)

avg_ortg = filtered[off_col].mean()
avg_drtg = filtered[def_col].mean()
avg_net = filtered["Net Rating"].mean()
player_count = filtered["Player"].nunique()

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Ortalama ORtg</div>
        <div class="card-value">{avg_ortg:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Ortalama DRtg</div>
        <div class="card-value">{avg_drtg:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    cls = "good" if avg_net >= 0 else "bad"
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Ortalama Net Rating</div>
        <div class="card-value {cls}">{avg_net:+.1f}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Oyuncu</div>
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

st.subheader("Oyuncu verimlilik haritası")
label_mode = st.radio("Oyuncu etiketleri", ["Seçili oyuncu", "En yüksek net rating: 10", "Tümü"], horizontal=True)

plot_data = filtered.copy()
plot_data["Label"] = ""
if label_mode == "Tümü":
    label_rows = plot_data.index
elif label_mode == "En yüksek net rating: 10":
    label_rows = plot_data.nlargest(10, "Net Rating").index
else:
    label_rows = plot_data[plot_data["Player"] == selected_player].index
plot_data.loc[label_rows, "Label"] = plot_data.loc[label_rows].apply(
    lambda r: f"{r['Player']}<br>{r['Net Rating']:+.1f}", axis=1)

fig = px.scatter(plot_data, x=off_col, y=def_col, color="Team",
    size=minute_col, text="Label", hover_name="Player",
    custom_data=["Team", "Net Rating", minute_col, game_col], size_max=32,
    color_discrete_map=TEAM_COLORS)
fig.update_traces(textposition="top center", textfont=dict(size=11, color="#f1d75c"),
    marker=dict(opacity=.85, line=dict(width=1, color="#e8edf7")),
    hovertemplate="<b>%{hovertext}</b> · %{customdata[0]}<br>ORtg %{x:.1f} / DRtg %{y:.1f}"
    "<br>Net rating: %{customdata[1]:+.1f}<br>Dakika: %{customdata[2]:.1f}"
    " · Maç: %{customdata[3]:.0f}<extra></extra>")

# Keep the reference fixed to all players even when a team is selected.
center_x, center_y = df[off_col].mean(), df[def_col].mean()
span_x = max(abs(filtered[off_col] - center_x).max() * 1.20, 15)
span_y = max(abs(filtered[def_col] - center_y).max() * 1.25, 12)
xlo, xhi = center_x - span_x, center_x + span_x
ylo, yhi = center_y - span_y, center_y + span_y
for xa, xb, ya, yb, color in [
    (center_x,xhi,ylo,center_y,"rgba(115,218,176,.035)"),
    (xlo,center_x,center_y,yhi,"rgba(255,142,151,.025)")]:
    fig.add_shape(type="rect",x0=xa,x1=xb,y0=ya,y1=yb,
                  fillcolor=color,line_width=0,layer="below")
fig.add_vline(x=center_x, line_color="#b2bdd3", line_width=1)
fig.add_hline(y=center_y, line_color="#b2bdd3", line_width=1)
# ORtg = DRtg is the actual zero-net line (not the mean crosshair).
low, high = max(xlo,ylo), min(xhi,yhi)
if low < high:
    fig.add_shape(type="line",x0=low,y0=low,x1=high,y1=high,
                  line=dict(color="rgba(182,194,217,.35)",width=1,dash="dot"),layer="below")
for x,y,text,anchor in [
    (.015,.98,"DÜŞÜK ORtg · DÜŞÜK DRtg","left"),
    (.985,.98,"YÜKSEK ORtg · DÜŞÜK DRtg","right"),
    (.015,.02,"DÜŞÜK ORtg · YÜKSEK DRtg","left"),
    (.985,.02,"YÜKSEK ORtg · YÜKSEK DRtg","right")]:
    fig.add_annotation(x=x,y=y,xref="paper",yref="paper",text=text,
        showarrow=False,xanchor=anchor,font=dict(size=10,color="#bac5db"),
        bgcolor="#19213a",borderpad=5)
if selected_player != "All":
    hp = filtered[filtered["Player"] == selected_player]
    fig.add_trace(go.Scatter(x=hp[off_col],y=hp[def_col],mode="markers",
        marker=dict(size=38,color="rgba(0,0,0,0)",line=dict(color="#f1d75c",width=3)),
        showlegend=False,hoverinfo="skip"))
fig.update_xaxes(range=[xlo,xhi],title="ORtg →",showgrid=False,zeroline=False,
                 tickfont=dict(color="#8f9db9",size=11))
fig.update_yaxes(range=[yhi,ylo],title="DRtg (düşük daha iyi)",showgrid=False,
                 zeroline=False,tickfont=dict(color="#8f9db9",size=11))
fig.update_layout(height=790,paper_bgcolor="#19213a",plot_bgcolor="#19213a",
    font=dict(color="#f6f7fb",family="Arial"),margin=dict(l=55,r=30,t=35,b=90),
    hoverlabel=dict(bgcolor="#101629",font_color="#f6f7fb"),
    legend=dict(title="",orientation="h",y=-.13,x=.5,xanchor="center",font_size=11))
st.plotly_chart(fig,use_container_width=True,theme=None,
    config={"displaylogo":False,"toImageButtonOptions":{"format":"png",
            "filename":"euroleague_player_landscape","width":1400,"height":1000,"scale":2}})

st.subheader("Oyuncuları karşılaştır")

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
            plot_bgcolor="#19213a",
            font=dict(color="white"),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )

        st.plotly_chart(fig_selected_players, use_container_width=True, theme=None)

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
            plot_bgcolor="#19213a",
            font=dict(color="white"),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )

        st.plotly_chart(fig_highlight_players, use_container_width=True, theme=None)

st.subheader("Team Comparison — Oyuncu Rating Ortalamaları")

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
            title="Selected Teams — Ortalama Net Rating"
        )

        fig_team_bar.update_layout(
            height=480,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#19213a",
            font=dict(color="white")
        )

        st.plotly_chart(fig_team_bar, use_container_width=True, theme=None)

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
            plot_bgcolor="#19213a",
            font=dict(color="white"),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )

        st.plotly_chart(fig_team_highlight, use_container_width=True, theme=None)

st.subheader("Net rating sıralaması")

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

st.subheader("Oyuncu ortalamaları")
average_labels = {
    "Player": "Oyuncu", "Team": "Takım", "GP": "Maç", "MPG": "Dakika",
    "PPG": "Sayı", "RPG": "Ribaund", "APG": "Asist", "SPG": "Top çalma",
    "BPG": "Blok", "TOV": "Top kaybı", "ORB": "Hücum rib.", "DRB": "Savunma rib.",
    "PF": "Faul", "FGM": "İsabet", "FGA": "Şut denemesi",
    "3PM": "3S isabet", "3PA": "3S denemesi", "FTM": "SA isabet", "FTA": "SA denemesi"
}
avg_columns = [c for c in average_labels if c in filtered.columns]
if "PPG" in filtered.columns:
    average_view = filtered[avg_columns].sort_values("PPG", ascending=False).copy()
    if selected_player != "All":
        player_row = filtered[filtered["Player"] == selected_player].iloc[0]
        st.markdown(f"**{selected_player} · Maç başına**")
        stats = st.columns(5)
        for container, column in zip(stats, ["MPG", "PPG", "RPG", "APG", "SPG"]):
            container.metric(average_labels[column], f"{player_row[column]:.1f}")
    basic_tab, shooting_tab = st.tabs(["Maç başına ortalamalar", "Şut ortalamaları"])
    for tab, columns in [
        (basic_tab, ["Player","Team","GP","MPG","PPG","RPG","APG","SPG","BPG","TOV","ORB","DRB","PF"]),
        (shooting_tab, ["Player","Team","GP","MPG","PPG","FGM","FGA","3PM","3PA","FTM","FTA"])
    ]:
        with tab:
            view = average_view[[c for c in columns if c in average_view]].rename(columns=average_labels)
            config = {average_labels[c]: st.column_config.NumberColumn(average_labels[c], format="%.1f")
                      for c in columns if c not in ["Player","Team","GP"] and c in average_view}
            st.dataframe(view, use_container_width=True, hide_index=True,
                         column_config=config, height=530)
    st.download_button("Ortalamaları CSV olarak indir",
        average_view.rename(columns=average_labels).to_csv(index=False).encode("utf-8-sig"),
        file_name="euroleague_oyuncu_ortalamalari.csv", mime="text/csv")
else:
    st.info("Oyuncu ortalamaları için güncel veri dosyasını yükleyin.")
