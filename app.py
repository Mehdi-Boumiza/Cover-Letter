import streamlit as st
import requests
import os 
from fpdf import FPDF
import re
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime
import json
from dotenv import load_dotenv

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

load_dotenv()
service_account_info = json.loads(os.getenv["credentials"])
groq_api_key = os.getenv("GROQ_API_KEY")
creds = Credentials.from_service_account_info(service_account_info,scopes = scope)
client = gspread.authorize(creds)

sheet = client.open("cover").sheet1

st.set_page_config(page_title= "Cover Letter Generator",page_icon='logo.png', layout="centered")

email = st.text_input("Enter Your email to receive your cover letter:")


def pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto = True, margin = 15)
    pdf.set_font("Arial", size = 12)

    for line in text.split("\n"):
        pdf.multi_cell(0,10,line)
    return pdf.output(dest= 'S').encode('latin1')


def valid_email(email):
    pattern = r"[^@]+@[^@]+\.[^@]+"
    return re.match(pattern, email)

st.markdown("<h1 style = 'text-align: center; color: #4CAF50;'> Cover Letter Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style = 'text-align: center; font-size: 18px;'> Generate personalized cover letter using your resume and job description.</p>", unsafe_allow_html=True)
st.write("")

resume, job_desc = st.columns(2)
with resume:
    resume_txt = st.text_area("Paste Your Resume", height = 200, placeholder="e.g Experience, Skills, Education...")
with job_desc:
    job_txt = st.text_area("Paste Job Description", height=200, placeholder="e.g Company role Requirements...")
st.write("")

if st.button("Generate Cover Letter"):
        if not valid_email(email):
            st.warning("Please Enter a valid email address.")
        elif not resume_txt or not job_txt:
            st.warning("Please Enter your resume and the job description.")
        else: 
            with st.spinner("Generating Your Cover Letter ..."):
                api_key = st.secrets["GROQ_API_KEY"]
                headers = {
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json"
                }
                prompt = f"""
        You are a professional career coach. Based on the resume and job description below, write a strong, customized cover letter for the user to apply for the job.

        Resume:
        {resume}

        Job Description:
        {job_desc}

        Cover Letter:
        """            
                data = {
                    "model" : "meta-llama/llama-4-scout-17b-16e-instruct",
                    "messages" : [{"role": "user", 'content': prompt}],
                    "max_tokens": 1024    
                }
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers = headers, json = data)
                try: 
                    result = response.json()
                    output = result.get('choices', [{}])[0].get('message', {}).get('content', 'Something went wrong. Check logs.')
                except Exception as e:
                    output = f"ERROR: {e}"
                st.success("DONE")
                st.text_area("Your Generated Cover Letter", output , height = 300)

                if email and valid_email(email):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sheet.append_row([email,timestamp])

                pdf_bytes = pdf(output)
                st.download_button(
                    label = 'Download as PDF',
                    data = pdf_bytes,
                    file_name="cover_letter.pdf",
                    mime='application/pdf'
                )



st.markdown("---")
st.markdown("<p style = 'text-align: center; color: gray;'>Built to help people fulfill their professional duties</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### About Me")
    st.markdown("""
Hey there! I'm a teenager passionate about AI and coding.

I built this app to help job seekers quickly generate professional cover letters with the power of AI and to learn while building something useful.

** Skills **  
Python • Streamlit • AI APIs • Web Apps • Prompt Engineering • Javascript • Mediapipe • AI Model development

** Contact Me **  
 Email:   mehdi.boumizaa@gmail.com
 Twitter: https://x.com/Mehdey_  
 LinkedIn: https://www.linkedin.com/in/mehdi-boumiza-42457035a/
 Github:   https://github.com/Mehdi-Boumiza

If this tool helped you or inspired you, feel free to connect!
""")
