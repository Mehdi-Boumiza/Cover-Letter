import streamlit as st
import requests
import os 


st.set_page_config(page_title= "Cover Letter Generator",page_icon='logo.png', layout="centered")


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
        with st.spinner("Generating Your Cover Letter ..."):
            api_key = os.environ.get("GROQ_API_KEY")
            headers = {
                "Authorization": f"Bearer {api_key}",
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
                "messages" : [
                    {"role": "user", 'content': prompt}
                ]

            }
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers = headers, json = data)
            try: 
                result = response.json()
                output = result.get('choices', [{}])[0].get('message', {}).get('content', 'Something went wrong. Check logs.')
            except Exception as e:
                 output = f"ERROR: {e}"
            st.success("DONE")
            st.text_area("Your Generated Cover Letter", output , height = 300)



st.markdown("---")
st.markdown("<p style = 'text-align: center; color: gray;'>Built to help people fulfill their professional duties</p>", unsafe_allow_html=True)