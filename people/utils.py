import re
import threading
import requests
import json
from PyPDF2 import PdfReader
import nltk
from nltk import pos_tag, ne_chunk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.data import find

nltk_lock = threading.Lock()

def download_nltk_data():
    try:
        find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)

    try:
        find('corpora/stopwords.zip')
    except LookupError:
        nltk.download('stopwords', quiet=True)

    try:
        find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger', quiet=True)

    try:
        find('corpora/wordnet.zip')
    except LookupError:
        nltk.download('wordnet', quiet=True)

    try:
        find('chunkers/maxent_ne_chunker')
    except LookupError:
        nltk.download('maxent_ne_chunker', quiet=True)

    try:
        find('corpora/words.zip')
    except LookupError:
        nltk.download('words', quiet=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_lightcast_access_token(client_id: str, client_secret: str) -> str:
    url = "https://auth.emsicloud.com/connect/token"
    payload = f"client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials&scope=emsi_open"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    if response.ok:
        return response.json()["access_token"]
    else:
        raise Exception("Failed to get access token")

def extract_lightcast_skills(access_token: str, resume_text: str, confidence_threshold: int = 0) -> list:
    url = "https://emsiservices.com/skills/versions/latest/extract"
    payload = {"text": resume_text, "confidenceThreshold": confidence_threshold}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.ok:
        skills_data = response.json().get("data", [])
        specialized_skills = []
        for skill_data in skills_data:
            skill = skill_data.get("skill", {})
            skill_type = skill.get("type", {})
            if skill_type.get("name") == "Specialized Skill":
                specialized_skills.append(skill["name"])
        return specialized_skills
    else:
        raise Exception("Failed to extract skills")

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize_and_process(text):
    with nltk_lock:
        download_nltk_data()
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        processed_tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    return processed_tokens

def extract_personal_info(resume_text):
    name = None
    email = None

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    download_nltk_data()
    with nltk_lock:
        tokens = word_tokenize(resume_text)
        pos_tags = pos_tag(tokens)

    chunks = ne_chunk(pos_tags)
    for chunk in chunks:
        if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
            name = ' '.join(c[0] for c in chunk)
            break
    matches = re.findall(email_pattern, resume_text)
    if matches:
        email = matches[0]

    return name, email

def process_resume(pdf_path, client_id, client_secret):
    try:
        resume_text = extract_text_from_pdf(pdf_path)
        preprocessed_text = preprocess_text(resume_text)
        tokens = tokenize_and_process(preprocessed_text)

        access_token = get_lightcast_access_token(client_id, client_secret)
        specialized_skills = extract_lightcast_skills(access_token, resume_text)

        name, email = extract_personal_info(resume_text)

        return {
            "name": name,
            "email": email,
            "topSkills": specialized_skills[:5],
            "otherSkills": specialized_skills[5:]
        }
    except Exception as e:
        print(f"Error processing resume: {e}")
        raise
