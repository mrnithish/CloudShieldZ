import streamlit as st
import os
import google.generativeai as genai
from api_key import api_key  # Import API key securely

# Configure Gemini API key
os.environ["GEMINI_API_KEY"] = api_key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Set up generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="""Data Ingestion:
Read the CSV file(s) containing vulnerability data for cloud-native applications.
Ensure that all necessary columns are present, including: Vulnerability ID, Violation Type, Impacted Service, Severity Level, Description of Issue, Container Health Status, Date Detected, Remediation Status, Compliance Impact, Exploitability Score, Attack Vector, Detection Method, Application Layer, Number of Affected Containers, Runtime Environment, Resource Utilization (CPU, Memory), Privileged Container Flag, Misconfiguration Detected, Encryption Status, Lateral Movement Potential, External Exposure, and Zero-Day Vulnerability.
... (other instructions)
""",
)

st.title("Cloud ShieldZ")
st.write("Upload one or more CSV files containing vulnerability data for analysis.")

# File uploader for multiple files
uploaded_files = st.file_uploader("Upload your CSV files", type="csv", accept_multiple_files=True)

# Text box for additional user instructions
user_instructions = st.text_area("Enter additional instructions for Gemini AI (optional):")

# Initialize session state variables
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

# Proceed only if files are uploaded
if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")
    
    # Read and concatenate content from all files
    combined_file_content = ""
    for uploaded_file in uploaded_files:
        file_content = uploaded_file.read().decode("utf-8")
        combined_file_content += f"\nFile: {uploaded_file.name}\n{file_content}\n"

    # Define the input message including all file contents and additional instructions
    input_message = (
        f"Analyze the following vulnerability data from multiple files:\n{combined_file_content}"
        f"\n\nAdditional Instructions:\n{user_instructions}"
    )
    
    # Initial submit button for analysis
    if st.button("Submit to Gemini AI"):
        # Send initial message to Gemini AI
        response = st.session_state.chat_session.send_message(input_message)
        
        # Display the response with formatting
        if response:
            st.subheader("Cloud ShieldZ")
            
            # Extract text content
            result_text = getattr(response, "text", "No text result provided.")
            st.write(result_text)
            
            # Check if there are any images and display them
            if hasattr(response, "images"):
                for image in response.images:
                    st.image(image, caption="Analysis Visualization", use_column_width=True)
            else:
                st.write("No images provided in the response.")
            
            # Display reference link if available
            reference_link = getattr(response, "reference_link", None)
            if reference_link:
                st.markdown(f"[Reference link]({reference_link})")
            else:
                st.write("No reference link provided.")
            
            # Mark analysis as complete
            st.session_state.analysis_complete = True
        else:
            st.error("Failed to retrieve a response from Gemini AI.")

# Show follow-up question section only after initial analysis
if st.session_state.analysis_complete:
    st.write("---")
    st.subheader("Ask Follow-up Questions to Gemini AI")

    # Input for follow-up questions
    follow_up_question = st.text_input("Enter your question for Gemini AI:")

    # Button to submit the follow-up question
    if st.button("Ask Follow-up Question"):
        if follow_up_question:
            # Send follow-up question to Gemini AI
            follow_up_response = st.session_state.chat_session.send_message(follow_up_question)
            
            # Display the follow-up response
            if follow_up_response:
                st.write("Gemini AI Response:")
                st.write(follow_up_response.text)
            else:
                st.error("Failed to retrieve a response for your follow-up question.")
        else:
            st.warning("Please enter a question before submitting.")
