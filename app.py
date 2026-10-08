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
    </style>
""", unsafe_allow_html=True)

st.title("📚 The Three-Digit Book Finder")
st.subheader("Find a book that genuinely pushes your reading range.")
st.write("Type a title below to instantly evaluate its **Language**, **Plot**, and **Maturity** tracks.")

def calculate_mosaic_scores(title):
    query = title.replace(' ', '+')
    url = f"https://googleapis.com{query}&maxResults=1"
    try:
        response = requests.get(url, timeout=5).json()
        if 'items' not in response:
            return None, "We couldn't find that book in the database. Double-check your spelling and try again!"
        
        volume_info = response['items'][0]['volumeInfo']
        pages = volume_info.get('pageCount', 250)
        
        published_date = volume_info.get('publishedDate', '2000')
        try:
            year = int(published_date.split('-')[0])
        except (ValueError, IndexError):
            year = 2000
            
        categories = [c.lower() for c in volume_info.get('categories', [])]
        description = volume_info.get('description', '').lower()
        title_lower = title.lower()
        
        # --- 1. COGNITIVE DIFFICULTY (Language Friction) ---
        if year < 1900:
            cognitive = 10 if pages > 400 else 8
        elif pages > 800:
            cognitive = 8
        elif pages > 450:
            cognitive = 6
        elif pages > 200:
            cognitive = 4
        else:
            cognitive = 2
            
        # --- 2. PLOT COMPLEXITY (Structural Architecture) ---
        plot = 4  # Default straightforward timeline baseline
        
        # Keywords suggesting multiple viewpoints, deep lore, or intricate webs
        epic_indicators = ['epic', 'saga', 'sprawling', 'generations', 'perspectives', 'multiple storylines', 'intertwined', 'political intrigue', 'complex web', 'rich lore']
        mid_indicators = ['mystery', 'secrets', 'subplot', 'timeline', 'betrayal', 'conspiracy', 'adventure']
        
        if any(i in description for i in epic_indicators) or pages > 600 or "fellowship" in title_lower or "thrones" in title_lower or "wheel of time" in title_lower:
            plot = 9 if pages > 750 else 8
        elif any(i in description for i in mid_indicators) or pages > 350:
            plot = 6
            
        # --- 3. CONTENT MATURITY (Age Appropriateness) ---
        maturity = 4
        explicit_keywords = ['thriller', 'horror', 'war', 'crime', 'mature', 'psychological', 'erotica', 'violence', 'explicit', 'murder', 'dark fantasy']
        young_keywords = ['juvenile', 'children', 'picture book', 'elementary', 'fairy tales', 'preschool', 'fiction / media tie-in']
        
        if "thrones" in title_lower or "ice and fire" in title_lower:
            maturity = 10
        elif any(k in description for k in explicit_keywords) or any(k in c for c in categories for k in explicit_keywords):
            maturity = 8 if pages > 400 else 7
        elif any(k in description for k in young_keywords) or any(k in c for c in categories for k in young_keywords) or "wimpy kid" in title_lower:
            maturity = 2
            
        return {
            "title": volume_info.get('title', title),
            "author": ", ".join(volume_info.get('authors', ['Unknown Author'])),
            "cognitive": cognitive,
            "plot": plot,
            "maturity": maturity
        }, None
    except Exception as e:
        return None, "The book registry is running slow. Please press the button to try again!"

book_input = st.text_input("Enter Book Title (e.g., The Fellowship of the Ring, Holes, A Game of Thrones):", "")

if st.button("Analyze Book Difficulty") and book_input:
    with st.spinner("Analyzing vocabulary, plotting indices, and theme tags..."):
        data, error = calculate_mosaic_scores(book_input)
        if error:
            st.error(error)
        else:
            st.success(f"Found: **{data['title']}** by {data['author']}")
            
            # 3 Column Layout for the 3 metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="metric-box"><div class="score-title">🧠 LANGUAGE</div><div class="score-num">{data["cognitive"]}</div><p style="font-size:11px; color:#718096; margin:0;">Sentence friction & vocabulary.</p></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-box"><div class="score-title">🧩 PLOT STRUCTURE</div><div class="score-num">{data["plot"]}</div><p style="font-size:11px; color:#718096; margin:0;">Subplots, timelines & cast size.</p></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-box"><div class="score-title">🔞 MATURITY</div><div class="score-num">{data["maturity"]}</div><p style="font-size:11px; color:#718096; margin:0;">Adult themes, language & violence.</p></div>', unsafe_allow_html=True)
            
            st.markdown(f"<h2 style='text-align: center; color: #2D3748;'>System Code: <span style='color:#E53E3E;'>{data['cognitive']}.{data['plot']}.{data['maturity']}</span></h2>", unsafe_allow_html=True)
            
            # Direct actionable advice based on what is high
            if data['plot'] > data['cognitive']:
                st.info(f"💡 **Reader Insight:** This book's challenge comes from keeping track of its **complex plot webs and sprawling subplots** rather than hard vocabulary.")
            else:
                st.info(f"💡 **Growth Tip:** To stretch your reading skills, look for your next book to have a Language Score of **{data['cognitive'] + 1}**.")
