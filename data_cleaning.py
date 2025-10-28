import pandas as pd
import re
import nltk
import spacy
from nltk.corpus import stopwords

# ===============================
# LOAD YOUR SCRAPED CSV
# ===============================
INPUT_FILE = "reddit_data.csv"  # change to your actual scraped CSV name
OUTPUT_FILE = "reddit_data_cleaned.csv"

# ===============================
# DOWNLOAD RESOURCES (once)
# ===============================
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
nlp = spacy.load("en_core_web_sm")

# ===============================
# TEXT CLEANING FUNCTIONS
# ===============================
def clean_text(text):
    if not isinstance(text, str):
        return ""

    # 1️⃣ Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # 2️⃣ Remove mentions and hashtags
    text = re.sub(r"@\w+|#\w+", "", text)

    # 3️⃣ Remove non-alphabetic characters except spaces
    text = re.sub(r"[^A-Za-z\s]", "", text)

    # 4️⃣ Lowercase everything
    text = text.lower().strip()

    # 5️⃣ Tokenize and remove stopwords
    tokens = [w for w in text.split() if w not in stop_words]

    # 6️⃣ Lemmatize using spaCy
    doc = nlp(" ".join(tokens))
    tokens = [token.lemma_ for token in doc]

    # 7️⃣ Join back to string
    return " ".join(tokens)

# ===============================
# LOAD, CLEAN, STRUCTURE
# ===============================
print(f"Loading {INPUT_FILE}...")
df = pd.read_csv(INPUT_FILE, encoding="utf-8")

# Combine Title + Selftext
df["text_combined"] = (df["Title"].fillna('') + " " + df["Selftext"].fillna('')).str.strip()

# Clean the text
print("Cleaning text...")
df["Cleaned_Text"] = df["text_combined"].apply(clean_text)

# Remove duplicates and short posts
df.drop_duplicates(subset=["Cleaned_Text"], inplace=True)
df = df[df["Cleaned_Text"].str.len() > 20]

# Keep relevant columns
df_final = df[["Title", "Cleaned_Text", "Author", "Score", "Comments", "Created_UTC", "URL"]]

# ===============================
# SAVE CLEANED CSV
# ===============================
df_final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"\n Cleaned data saved to: {OUTPUT_FILE}")
print(f"Total rows before: {len(df)} | After cleaning: {len(df_final)}")
