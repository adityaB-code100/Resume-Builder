
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import os
import json
from dotenv import load_dotenv
from helper import configure_genai, get_gemini_response, extract_pdf_text, prepare_prompt

# Skill to company mapping
skill_set = {
    'java': ["Google", "Microsoft", "Capgemini"],
    'python': ["Google", "Microsoft", "Capgemini", "DeepSeek"],
    'machinelearning': ["Google", "Microsoft"],
    'c': ["Google", "Microsoft", "OpenAI"],
    'javascript': ["Google", "Microsoft", "Capgemini", "OpenAI"]
}

def init_session_state():
    if 'processing' not in st.session_state:
        st.session_state.processing = False

def display_sidebar():
    with st.sidebar:
        st.title("🎯 AI-Powered Resume")
        st.markdown("🚀 *AI-powered Resume & JD Analyzer*")
        st.subheader("📌 Features")
        st.markdown("""
        - Evaluate resume-job description match
        - Highlight missing keywords
        - Generate improvement suggestions
        """)
        add_vertical_space(2)

def match_skills_with_companies(skills):
    matched = set()
    normalized_skills = [s.strip().lower() for s in skills]

    for skill in normalized_skills:
        for key in skill_set:
            if key in skill:  # partial match logic
                matched.update(skill_set[key])

    st.subheader("🏢 Matched Companies Based on Skills")
    if matched:
        st.write(", ".join(matched))
    else:
        st.write("❌ No companies match the listed skills.")

def analyze_resume(resume_file, jd):
    resume_text = extract_pdf_text(resume_file)
    input_prompt = prepare_prompt(resume_text, jd)
    response = get_gemini_response(input_prompt)
    data = json.loads(response)
    return data

def main():
    load_dotenv()
    init_session_state()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Please set the GOOGLE_API_KEY in your `.env` file.")
        return

    try:
        configure_genai(api_key)
    except Exception as e:
        st.error(f"❌ Gemini API configuration failed: {str(e)}")
        return

    display_sidebar()
    
    st.title("📄 AI-Powered Resume Tailoring And Job Matching Platform")
    st.subheader("🎯 Optimize Your Resume for Job Descriptions")

    jd = st.text_area("📝 Job Description")
    uploaded_files = st.file_uploader("📤 Upload Resumes (PDFs)", type=["pdf"], accept_multiple_files=True)
    user_skills_input = st.text_input("💡 Enter Your Skills (comma-separated)", placeholder="e.g., Python, Java, MachineLearning")
    user_skills = [s.strip().lower() for s in user_skills_input.split(",") if s.strip()]

    if st.button("🔍 Analyze Resumes", disabled=st.session_state.processing):
        if not jd or not uploaded_files:
            st.warning("⚠️ Please enter job description and upload at least one resume.")
            return

        st.session_state.processing = True

        try:
            with st.spinner("📊 Analyzing your resumes..."):
                all_results = []
                for resume_file in uploaded_files:
                    data = analyze_resume(resume_file, jd)
                    all_results.append({
                        'resume': resume_file,
                        'match_score': data.get("JD Match", 0),
                        'profile_summary': data.get("Profile Summary", "N/A"),
                        'missing_keywords': data.get("MissingKeywords", []),
                        'extracted_skills': [s.strip().lower() for s in data.get("Extracted Skills", [])]
                    })

                all_results.sort(key=lambda x: x['match_score'], reverse=True)

                num_resumes = st.number_input("🧑‍💻 How many resumes do you want to view?", 
                                              min_value=1, 
                                              max_value=len(uploaded_files),  
                                              value=min(3, len(uploaded_files)))  

                for idx, result in enumerate(all_results[:num_resumes]):
                    st.subheader(f"📄 Resume {idx + 1}")
                    st.write(f"**Match Score**: {result['match_score']}")
                    st.write(f"**Profile Summary**: {result['profile_summary']}")
                    st.write(f"**Missing Keywords**: {', '.join(result['missing_keywords']) if result['missing_keywords'] else '🎉 No missing keywords'}")
                    st.write(f"**Extracted Skills**: {', '.join(result['extracted_skills'])}")

                    match_skills_with_companies(result['extracted_skills'] + user_skills)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
        finally:
            st.session_state.processing = False

if __name__ == "__main__":
    main()
