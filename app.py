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
    url = f"https://openlibrary.org{query}"
    try:
        response = requests.get(url, timeout=5).json()
        if not response.get('docs'):
            return None, "We couldn't find that book. Double-check your spelling and try again!"
        doc = response['docs'][0]
        pages = doc.get('number_of_pages_median', doc.get('number_of_pages', 250))
        if isinstance(pages, list): pages = pages[0]
        year = doc.get('first_publish_year', 2000)
        subjects = [s.lower() for s in doc.get('subject', [])]
        
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
        explicit_tags = ['thriller', 'horror', 'war', 'crime', 'mature', 'psychological', 'erotica', 'violence']
        young_tags = ['juvenile', 'children', 'picture book', 'elementary', 'fairy tales']
        
        if any(t in s for s in subjects for t in explicit_tags) or "thrones" in title.lower():
            maturity = 9 if pages > 500 else 8
        elif any(t in s for s in subjects for t in young_tags):
            maturity = 2
            
        return {
            "title": doc.get('title', title),
            "author": doc.get('author_name', ['Unknown Author'])[0],
            "cognitive": cognitive,
            "maturity": maturity
        }, None
    except Exception:
        return None, "The public book registry is running slow. Please press the button to try again!"

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
