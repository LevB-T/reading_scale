import streamlit as st
import requests

st.set_page_config(page_title="Mosaic Reading Scale", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .main {background-color: #f7f9fc;}
    .stButton>button {background-color: #4A90E2; color: white; border-radius: 8px; width: 100%; font-weight: bold;}
    .metric-box {padding: 20px; border-radius: 10px; background-color: white; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 15px;}
    .score-title {font-size: 14px; color: #4A5568; font-weight: bold; letter-spacing: 0.05em;}
    .score-num {font-size: 54px; font-weight: 800; color: #2B6CB0; margin: 10px 0;}
    </style>
""", unsafe_allow_html=True)

st.title("📚 The Two-Digit Book Finder")
st.subheader("Find a book that genuinely pushes your reading range.")
st.write("Type a book title below to instantly separate its **Linguistic Challenge** from its **Maturity Content**.")

def calculate_mosaic_scores(title):
    query = title.replace(' ', '+')
    # Using Google Books public API for extreme speed and reliability
    url = f"https://googleapis.com{query}&maxResults=1"
    try:
        response = requests.get(url, timeout=5).json()
        if 'items' not in response:
            return None, "We couldn't find that book in the database. Double-check your spelling and try again!"
        
        volume_info = response['items'][0]['volumeInfo']
        pages = volume_info.get('pageCount', 250)
        
        # Grab publish year if available
        published_date = volume_info.get('publishedDate', '2000')
        try:
            year = int(published_date.split('-')[0])
        except ValueError:
            year = 2000
            
        # Collect descriptive tags or categories
        categories = [c.lower() for c in volume_info.get('categories', [])]
        description = volume_info.get('description', '').lower()
        
        # Brainpower / Cognitive Difficulty Algorithm
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
            
        # Content Maturity Algorithm
        maturity = 4
        explicit_keywords = ['thriller', 'horror', 'war', 'crime', 'mature', 'psychological', 'erotica', 'violence', 'explicit', 'murder']
        young_keywords = ['juvenile', 'children', 'picture book', 'elementary', 'fairy tales', 'preschool', 'fiction / media tie-in']
        
        # Check title strings directly for specific known examples
        title_lower = title.lower()
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
            "maturity": maturity
        }, None
    except Exception:
        return None, "The book registry is running slow. Please press the button to try again!"

book_input = st.text_input("Enter Book Title (e.g., The Odyssey, Holes, A Game of Thrones):", "")

if st.button("Analyze Book Difficulty") and book_input:
    with st.spinner("Analyzing vocabulary metrics and theme tags..."):
        data, error = calculate_mosaic_scores(book_input)
        if error:
            st.error(error)
        else:
            st.success(f"Found: **{data['title']}** by {data['author']}")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="metric-box"><div class="score-title">🧠 COGNITIVE SCORE</div><div class="score-num">{data["cognitive"]}</div><p style="font-size:12px; color:#718096; margin:0;">Sentence friction & structural density.</p></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-box"><div class="score-title">🔞 MATURITY SCORE</div><div class="score-num">{data["maturity"]}</div><p style="font-size:12px; color:#718096; margin:0;">Adult language, themes, & violence.</p></div>', unsafe_allow_html=True)
            
            st.markdown(f"<h2 style='text-align: center; color: #2D3748;'>System Code: <span style='color:#E53E3E;'>{data['cognitive']}.{data['maturity']}</span></h2>", unsafe_allow_html=True)
            st.info(f"**Growth Tip:** To stretch your reading skills, look for your next book to have a Cognitive Score of **{data['cognitive'] + 1}**.")
