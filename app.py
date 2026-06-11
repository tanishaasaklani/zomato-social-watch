import streamlit as st
import pandas as pd
import json
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Zomato Social Watch",
    layout="wide"
)

st_autorefresh(interval=300000, key="refresh")

# ==================================================
# CSS
# ==================================================

st.markdown("""
<style>

.stApp{
    background-color:#0B1120;
}

div[data-testid="stSidebar"]{
    background-color:#08101F;
}

.card-high{
    background-color:#2B0B12;
    border:1px solid #8B1E3F;
    padding:18px;
    border-radius:15px;
    margin-bottom:15px;
}

.card-medium{
    background-color:#2A1A08;
    border:1px solid #A16207;
    padding:18px;
    border-radius:15px;
    margin-bottom:15px;
}

.card-low{
    background-color:#111827;
    border:1px solid #1F2937;
    padding:18px;
    border-radius:15px;
    margin-bottom:15px;
}

.score{
    color:#FF4B4B;
    font-size:24px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# LOAD DATA
# ==================================================

try:
    with open("classified_posts.json","r",encoding="utf-8") as f:
        posts = json.load(f)

except:
    posts = []

df = pd.DataFrame(posts)

# ==================================================
# CATEGORY LABELS
# ==================================================

if not df.empty:

    df["category_label"] = df["category"].replace({
        "urgent_safety_trust":"Safety",
        "delivery_operations":"Delivery",
        "app_product_issues":"Product",
        "viral_positive_mentions":"Positive",
        "competitor_intelligence":"Competitor",
        "irrelevant":"Irrelevant"
    })

# ==================================================
# SIDEBAR
# ==================================================


st.sidebar.markdown("## Zomato Social Watch")
st.sidebar.caption("AI Monitoring Platform")


page = st.sidebar.segmented_control(
    "",
    [
        ":material/home: Feed",
        ":material/warning: Escalations",
        ":material/analytics: Analytics",
        ":material/cable: Connectors"
    ]
)


# ==================================================
# HOME FEED PAGE
# ==================================================

if page == ":material/home: Feed":

    # ---------- HEADER ----------
    col1, col2, col3 = st.columns([1,2,1])

    st.markdown(
        """
        <h1 style='text-align:center;
                   font-size:48px;
                   font-weight:bold;'>
            Zomato Social Watch
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style='text-align:center;
                  color:gray;
                  font-size:18px;'>
            AI Monitoring Platform
        </p>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    st.caption(f"Monitoring {len(df)} posts for Zomato mentions")

    # ---------- FILTERS ----------
    col1, col2, col3, col4 = st.columns([3,1,1,1])

    with col1:
        search = st.text_input(
            "",
            placeholder="Search posts..."
        )

    with col2:
        source_filter = st.selectbox(
            "Source",
            ["All"] + sorted(df["source"].unique().tolist())
            if not df.empty else ["All"]
        )

    with col3:
        category_filter = st.selectbox(
            "Category",
            ["All"] + sorted(df["category_label"].unique().tolist())
            if not df.empty else ["All"]
        )

    with col4:
        priority_filter = st.selectbox(
            "Priority",
            ["All", "HIGH", "MEDIUM", "LOW"]
        )

    filtered_df = df.copy()

    if not filtered_df.empty:

        if search:
            filtered_df = filtered_df[
                filtered_df["text"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        if source_filter != "All":
            filtered_df = filtered_df[
                filtered_df["source"] == source_filter
            ]

        if category_filter != "All":
            filtered_df = filtered_df[
                filtered_df["category_label"] == category_filter
            ]

        if priority_filter != "All":
            filtered_df = filtered_df[
                filtered_df["priority"] == priority_filter
            ]

    # ---------- FEED ----------
    if filtered_df.empty:

        st.info("No posts found.")

    else:

        filtered_df = filtered_df.sort_values(
            by="score",
            ascending=False
        )

        for _, row in filtered_df.iterrows():

            source = str(row["source"]).lower()

            if source == "reddit":
                logo = "icons/reddit.png"

            elif source == "twitter":
                logo = "icons/x_logo.png"

            else:
                logo = "icons/rss.png"

            priority = row["priority"]

            if priority == "HIGH":
                css_class = "card-high"

            elif priority == "MEDIUM":
                css_class = "card-medium"

            else:
                css_class = "card-low"

            st.markdown(
                f'<div class="{css_class}">',
                unsafe_allow_html=True
            )

            c1, c2 = st.columns([1,10])

            with c1:
                st.image(logo, width=35)

            with c2:

                st.markdown(
                    f"**{row['author']}**"
                )

                timestamp = row["timestamp"]

                if timestamp == "None":
                    timestamp = "Recent"

                st.caption(timestamp)

            clean_text = (
                row["text"]
                .encode("utf-8", "ignore")
                .decode()
            )

            st.write(clean_text)

            st.caption(
                f"Category : {row['category_label']}"
            )

            st.caption(
                f"Priority : {row['priority']}"
            )

            st.caption(
                f"Default Action : {row['action']}"
            )

            st.markdown(
                f'<div class="score">{row["score"]}</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

# ==================================================
# ESCALATIONS PAGE
# ==================================================

elif page == "Escalations":

    st.title("Escalations")
    st.caption("High Priority Signals Requiring Immediate Attention")

    if df.empty:

        st.info("No escalations available.")

    else:

        high_df = df[
            df["priority"] == "HIGH"
        ].sort_values(
            by="score",
            ascending=False
        )

        if high_df.empty:

            st.info("No HIGH priority alerts found.")

        else:

            for _, row in high_df.iterrows():

                source = str(row["source"]).lower()

                if source == "reddit":
                    logo = "icons/reddit.png"

                elif source == "twitter":
                    logo = "icons/x_logo.png"

                else:
                    logo = "icons/rss.png"

                st.markdown(
                    '<div class="card-high">',
                    unsafe_allow_html=True
                )

                c1, c2 = st.columns([1,10])

                with c1:
                    st.image(logo, width=35)

                with c2:

                    st.markdown(
                        f"**{row['author']}**"
                    )

                    timestamp = row["timestamp"]

                    if timestamp == "None":
                        timestamp = "Recent"

                    st.caption(timestamp)

                st.write(row["text"])

                st.markdown(
                    f'<div class="score">{row["score"]}</div>',
                    unsafe_allow_html=True
                )

                st.caption(
                    f"Category : {row['category_label']}"
                )

                st.caption(
                    f"Action : {row['action']}"
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

# ==================================================
# ANALYTICS PAGE
# ==================================================

elif page == "Analytics":

    st.title("Analytics")
    st.caption("Platform Intelligence Dashboard")

    if df.empty:

        st.info("No analytics data available.")

    else:

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Source Distribution")

            source_counts = (
                df["source"]
                .value_counts()
            )

            st.bar_chart(source_counts)

        with col2:

            st.subheader("Priority Distribution")

            priority_counts = (
                df["priority"]
                .value_counts()
            )

            st.bar_chart(priority_counts)

        st.divider()

        st.subheader("Category Distribution")

        category_counts = (
            df["category_label"]
            .value_counts()
        )

        st.bar_chart(category_counts)

        st.divider()

        st.subheader("Top 5 Escalations")

        top5 = (
            df.sort_values(
                by="score",
                ascending=False
            )
            .head(5)
        )

        st.dataframe(
            top5[
                [
                    "author",
                    "source",
                    "priority",
                    "score"
                ]
            ],
            use_container_width=True
        )


# ==================================================
# CONNECTORS PAGE
# ==================================================

elif page == "Connectors":

    st.title("Connectors")
    st.caption("External Data Sources")

    # ---------- Reddit ----------

    with st.container():

        c1, c2 = st.columns([1,5])

        with c1:
            st.image("icons/reddit.png", width=40)

        with c2:
            st.markdown("### Reddit")
            st.success("ONLINE")

    # ---------- X ----------

    with st.container():

        c1, c2 = st.columns([1,5])

        with c1:
            st.image("icons/x_logo.png", width=40)

        with c2:
            st.markdown("### X / Twitter")
            st.success("ONLINE")

    # ---------- RSS ----------

    with st.container():

        c1, c2 = st.columns([1,5])

        with c1:
            st.image("icons/rss.png", width=40)

        with c2:
            st.markdown("### RSS News")
            st.success("ONLINE")

# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    f"""
Feed Status : ACTIVE

Last Refresh : {datetime.now().strftime('%I:%M %p')}

"""
)