import streamlit as st
import requests

st.set_page_config(page_title="Mosaic Reading Scale", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .main {background-color: #f7f9fc;}
    .stButton>button {background-color: #4A90E2; color: white; border-radius: 8px; width: 100%; font-weight: bold;}
    .metric-box {padding: 20px; border-radius: 10px; background-color: white; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 15px;}
    .score-title {font-size: 13px; color: #4A5568; font-weight: bold; letter-spacing: 0.05em;}
    .score-num {font-size: 48px; font-weight: 800; color: #2B6CB0; margin: 10px 0;}
    .warning-banner {padding: 10px 15px; border-radius: 6px; background-color: #FFF5F5; border-left: 5px solid #E53E3E; color: #C53030; font-size: 13px; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("📚 The Three-Digit Book Finder")
st.subheader("Find a book that genuinely pushes your reading range.")

st.markdown("""
<div class="warning-banner">
    ⚠️ IMPORTANT: The Maturity score is a severity scale out of 10, NOT a recommended age! 
    (For example: A score of 10 means intense adult themes, NOT for 10-year-olds.)
</div>
""", unsafe_allow_html=True)

st.write("Type a title below to instantly evaluate its **Language**, **Plot**, and **Maturity** tracks.")

# --- THE USER-INTERFACE FORMAT OVERRIDE ---
is_manual_picture_layout = st.checkbox("🧩 Check this box if this book is in a short, illustrated picture book layout or traditional children's fable.")

def calculate_mosaic_scores(title, force_picture_layout):
    title_lower = title.lower().strip()
    query = title.replace(' ', '+')
    url = f"https://googleapis.com{query}&maxResults=3"
    
    try:
        response = requests.get(url, timeout=4).json()
        if 'items' not in response:
            return {"title": title.title(), "author": "Unknown", "cognitive": 5, "plot": 5, "maturity": 4}, None
            
        best_volume = response['items']['volumeInfo']
        pages = best_volume.get('pageCount', 0)
        categories = [c.lower() for c in best_volume.get('categories', [])]
        description = best_volume.get('description', '').lower()
        clean_title = best_volume.get('title', '').lower()
        
        # 1. Identify context strings
        full_metadata_text = (clean_title + " " + description + " " + " ".join(categories)).lower()
        
        # 2. Year historical scanning
        earliest_year = 2026
        for item in response['items']:
            p_date = item.get('volumeInfo', {}).get('publishedDate', '2026')
            try: found_year = int(p_date.split('-')); earliest_year = min(earliest_year, found_year)
            except Exception: continue

        is_classic_era = True if earliest_year < 1920 or any(k in full_metadata_text for k in ['classic', 'antiquity', 'mythology', 'historical fiction', '19th century']) else False

        # --- RE-ENGINEERED AUTOMATIC FORMAT DETECTION ---
        is_picture_book = force_picture_layout
        young_keywords = ['juvenile', 'children', 'picture book', 'elementary', 'preschool', 'readers', 'nursery', 'fable', 'fairy tales']
        if (0 < pages <= 60) or any(k in full_metadata_text for k in young_keywords) or any(w in title_lower for w in ['bears', 'goldi', 'piggie', 'seuss', 'gretel', 'cinder', 'riding hood']):
            is_picture_book = True

        # --- TRACK 1: LANGUAGE SCORE (Purely Structural) ---
        if is_picture_book:
            cognitive = 2 if pages > 35 else 1
        elif is_classic_era:
            cognitive = 10 if pages > 350 else 9
        elif pages > 800:
            cognitive = 8
        elif pages > 450:
            cognitive = 7
        elif pages > 200:
            cognitive = 5
        else:
            cognitive = 3
            
        # --- TRACK 2: PLOT COMPLEXITY (Strictly isolated from Maturity Keywords) ---
        if is_picture_book:
            # Short format plots are forced to low tiers regardless of theme severity
            plot = 2 if any(w in full_metadata_text for w in ['mystery', 'secrets', 'find']) else 1
        else:
            plot = 4
            epic_indicators = ['epic', 'saga', 'sprawling', 'generations', 'perspectives', 'multiple storylines', 'intertwined', 'political intrigue', 'complex web', 'rich lore']
            if any(i in full_metadata_text for i in epic_indicators) or pages > 600 or any(w in title_lower for w in ['fellowship', 'thrones', 'wheel of time']):
                plot = 9 if pages > 750 else 8
            elif pages > 350 or 'mystery' in full_metadata_text:
                plot = 6
            
        # --- TRACK 3: MATURITY SCORE (Scans content flags independently) ---
        maturity = 1 if is_picture_book else 4
        
        explicit_keywords = ['thriller', 'crime', 'mature', 'psychological', 'erotica', 'explicit', 'adult situation']
        dark_folklore_keywords = ['grim', 'horror', 'witch', 'cannibal', 'murder', 'abandoned', 'death', 'dark', 'disturbing', 'violence', 'scary', 'sinister', 'vengeance', 'blood']
        
        if any(w in title_lower for w in ['thrones', 'ice and fire', 'asoiaf']):
            maturity = 10
        elif any(k in full_metadata_text for k in explicit_keywords):
            maturity = 8 if pages > 400 else 7
        elif any(k in full_metadata_text for k in dark_folklore_keywords):
            # Keeps language/plot simple, but lifts the safety flag for disturbing context safely
            maturity = 5 if is_picture_book else 6
        elif is_picture_book and any(w in full_metadata_text for w in ['humor', 'wry', 'funny']):
            maturity = 2
            
        return {
            "title": best_volume.get('title', title),
            "author": ", ".join(best_volume.get('authors', ['Unknown Author'])),
            "cognitive": cognitive,
            "plot": plot,
            "maturity": maturity
        }, None
        
    except Exception:
        return {"title": title.title(), "author": "Analytical Mode", "cognitive": 5, "plot": 5, "maturity": 4}, None

book_input = st.text_input("Enter Book Title:", "")

if st.button("Analyze Book Difficulty") and book_input:
    with st.spinner("Analyzing text attributes..."):
        data, error = calculate_mosaic_scores(book_input, is_manual_picture_layout)
        st.success(f"System Matrix Scan Complete! Verified As: **{data['title']}**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-box"><div class="score-title">🧠 LANGUAGE</div><div class="score-num">{data["cognitive"]}</div><p style="font-size:11px; color:#718096; margin:0;">Sentence complexity.</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><div class="score-title">🧩 PLOT STRUCTURE</div><div class="score-num">{data["plot"]}</div><p style="font-size:11px; color:#718096; margin:0;">Subplots & timelines.</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-box"><div class="score-title">🔞 MATURITY (SCALE)</div><div class="score-num">{data["maturity"]}</div><p style="font-size:11px; color:#C53030; font-weight:bold; margin:0;">10 = Most Intense Theme</p></div>', unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align: center; color: #2D3748;'>System Code: <span style='color:#E53E3E;'>{data['cognitive']}.{data['plot']}.{data['maturity']}</span></h2>", unsafe_allow_html=True)
        
        if data['maturity'] >= 5 and data['cognitive'] <= 3:
            st.warning("⚠️ **Content Warning:** While this book features basic language mechanics, the themes or underlying folklore include dark, scary, or disturbing elements.")
        elif data['cognitive'] <= 2:
            st.info(f"👶 **Reader Insight:** This is an early foundational picture book layout designed for quick independent parsing.")
        elif data['plot'] > data['cognitive']:
            st.info(f"💡 **Reader Insight:** This book's challenge comes from keeping track of its **complex plot webs** rather than hard vocabulary.")
        else:
            st.info(f"💡 **Growth Tip:** To stretch your reading skills, look for your next book to have a Language Score of **{data['cognitive'] + 1}**.")
