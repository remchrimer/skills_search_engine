import re
import requests
import json
from PyPDF2 import PdfReader
import nltk
import en_core_web_sm
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

ALLOWED_EXTENSIONS = {'pdf'}
nlp = en_core_web_sm.load()

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
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    processed_tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    return processed_tokens

def extract_personal_info(resume_text):
    name = None
    email = None

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    doc = nlp(resume_text)
    for ent in doc.ents:
        if ent.label_ == 'PERSON' and not name:
            name = ent.text

    matches = re.findall(email_pattern, resume_text)
    if matches:
        email = matches[0]

    return name, email

def process_resume(pdf_path, client_id, client_secret):
    resume_text = extract_text_from_pdf(pdf_path)
    preprocessed_text = preprocess_text(resume_text)
    tokens = tokenize_and_process(preprocessed_text)

    access_token = get_lightcast_access_token(client_id, client_secret)
    specialized_skills = extract_lightcast_skills(access_token, resume_text)

    name, email = extract_personal_info(resume_text)

    return {
        "tokens": tokens,
        "specialized_skills": specialized_skills,
        "name": name,
        "email": email
    }
