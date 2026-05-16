import streamlit as st
import re
import json
from pathlib import Path
from core.config import get_panel_dir, VOLUMES
from core.gcs_utils import list_valid_suttas, get_sutta_content
from core.embeddings import get_embedding, cosine_similarity

st.set_page_config(layout="wide", page_title="Dama Manga")

# Session State
if "sealed" not in st.session_state:
    st.session_state.sealed = set()
if "selected_nik" not in st.session_state:
    st.session_state.selected_nik = None
if "selected_bk" not in st.session_state:
    st.session_state.selected_bk = None
if "selected_sutta" not in st.session_state:
    st.session_state.selected_sutta = None

@st.cache_data
def get_hierarchy():
    suttas = list_valid_suttas()
    h = {}
    for s in suttas:
        m = re.match(r"([a-zA-Z]+)(\d+)", s.lower().replace(" ", ""))
        if m:
            nik, bk = m.group(1).upper(), m.group(2)
            h.setdefault(nik, {}).setdefault(bk, []).append(s)
    return h

hierarchy = get_hierarchy()
nik_list = sorted(hierarchy.keys())

# Initialize selections
if st.session_state.selected_nik is None:
    st.session_state.selected_nik = nik_list[0]
if st.session_state.selected_bk is None:
    bk_list = sorted(hierarchy[st.session_state.selected_nik].keys(), key=int)
    st.session_state.selected_bk = bk_list[0]
if st.session_state.selected_sutta is None:
    st.session_state.selected_sutta = hierarchy[st.session_state.selected_nik][st.session_state.selected_bk][0]

# Hardcode volume to buddha_v01
VOLUME = "buddha_v01"

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🏯 Dama Manga")
    st.metric("🔏 Sealed", len(st.session_state.sealed))
    st.divider()
    st.markdown("### 📚 Sutta Navigation")
    
    # Nikaya dropdown
    nik = st.selectbox("Nikaya", nik_list, index=nik_list.index(st.session_state.selected_nik))
    if nik != st.session_state.selected_nik:
        st.session_state.selected_nik = nik
        bk_list = sorted(hierarchy[nik].keys(), key=int)
        st.session_state.selected_bk = bk_list[0]
        st.session_state.selected_sutta = hierarchy[nik][bk_list[0]][0]
        st.rerun()
    
    # Book dropdown
    bk_list = sorted(hierarchy[nik].keys(), key=int)
    bk = st.selectbox("Book", bk_list, index=bk_list.index(st.session_state.selected_bk))
    if bk != st.session_state.selected_bk:
        st.session_state.selected_bk = bk
        st.session_state.selected_sutta = hierarchy[nik][bk][0]
        st.rerun()
    
    # Sutta dropdown
    sutta_list = hierarchy[nik][bk]
    sutta = st.selectbox("Sutta", sutta_list, index=sutta_list.index(st.session_state.selected_sutta))
    if sutta != st.session_state.selected_sutta:
        st.session_state.selected_sutta = sutta
        st.rerun()
    
    st.divider()
    st.caption(f"📍 {st.session_state.selected_nik} {st.session_state.selected_bk}")

# --- MAIN CONTENT ---
current_sutta = st.session_state.selected_sutta
sutta_data = get_sutta_content(current_sutta)

st.header(f"{current_sutta}: {sutta_data.get('title', '')}")

with st.expander("📖 View Sutta Text"):
    st.write(sutta_data.get('content', ''))

# --- MATCHING PANELS ---
def get_matches(sutta_text, sealed_set):
    panel_dir = get_panel_dir(VOLUME)
    if not panel_dir.exists():
        return []
    
    s_emb = get_embedding(sutta_text)
    matches = []
    
    for json_path in panel_dir.glob("*.json"):
        if json_path.stem in sealed_set:
            continue
        try:
            with open(json_path) as f:
                data = json.load(f)
            desc = data.get("descriptions", {}).get("modern", "")
            if desc:
                score = cosine_similarity(s_emb, get_embedding(desc))
                matches.append({
                    "path": str(json_path.with_suffix(".png")),
                    "score": score,
                    "id": json_path.stem,
                    "modern": data.get("descriptions", {}).get("modern", "N/A"),
                    "suttic": data.get("descriptions", {}).get("suttic_english", "N/A")
                })
        except:
            continue
    
    return sorted(matches, key=lambda x: x["score"], reverse=True)[:15]

with st.spinner("Finding matching panels..."):
    results = get_matches(
        f"{sutta_data.get('title', '')} {sutta_data.get('content', '')}",
        st.session_state.sealed
    )

# --- DISPLAY PANELS ---
if results:
    st.subheader(f"🖼️ Matching Panels ({len(results)})")
    
    cols = st.columns(5)
    for i, res in enumerate(results):
        with cols[i % 5]:
            # Image
            if Path(res['path']).exists():
                st.image(res['path'], use_container_width=True)
            
            # Description button
            with st.popover(f"📖 View Description", use_container_width=True):
                st.markdown("**Modern:**")
                st.write(res['modern'])
                st.markdown("**Suttic:**")
                st.write(res['suttic'])
            
            # Seal button
            if st.button(f"🔒 Seal", key=f"seal_{res['id']}", use_container_width=True):
                st.session_state.sealed.add(res['id'])
                st.rerun()
            
            st.caption(f"Score: {res['score']:.3f}")
else:
    st.info("No matching panels found for this sutta.")
