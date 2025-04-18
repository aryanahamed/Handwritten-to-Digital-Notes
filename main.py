import os
import time
import streamlit as st
from dotenv import load_dotenv
import requests
import google.generativeai as genai
import tempfile
import mimetypes
import random

load_dotenv()

st.title("Better Notes 📝", anchor=False)
st.caption("Upload a picture of your notes or take one. Choosing the wrong type will result in bad output.")
user_api_key = st.text_input("Enter your Gemini API Key (leave blank to use default and please don't abuse)", type="password")

gemini_api_key = None
if user_api_key:
    gemini_api_key = user_api_key
else:
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
else:
    st.error("Gemini API Key not found. Please provide one or set the GEMINI_API_KEY environment variable.")
    st.stop()

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 65536,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-preview-04-17",
    generation_config=generation_config,
)

spinner_messages = [
    "Cooking the notes... 🍳",
    "Brewing some knowledge... ☕",
    "Whipping up insights... 🥣",
    "Simmering the details... 🔥",
    "Grilling the concepts... ♨️",
    "Baking understanding... 🍞",
    "Mixing the main points... 🥄",
    "Seasoning the summary...🧂",
    "Decoding the scribbles... 🕵️",
    "Translating the hieroglyphs... 📜",
    "Assembling the ideas... 🧩",
    "Polishing the text... ✨",
]

url = "https://md-to-pdf.fly.dev"

css = '''
h1, h2 {
  	font-family:georgia, serif;
	color:#381704;
	font-size:24px;
	letter-spacing:0.1em;
	line-height:150%;
	padding-top:5px;
}
p {
  	font-family:georgia,serif;
	color:#381704;
	font-size:16px;
	font-weight:normal;
	line-height:150%;
	padding:0px;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 0 auto;
}
th, td {
	border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
}
th {
    background-color: #282a35;
    font-size: 18px;
	color:#fff;
	font-weight: bold;
}
td {
	font-size: 16px;
}
tr {
    border-bottom: 1px solid black;
}
'''

footer="""<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: black;
    color: white;
    text-align: center;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    padding: 10px;
}

.footer p {
    margin: 0;
}
</style>

<div class="footer">
    <p>Made with ❤ by Aryan</p>
</div>
"""

def stream_data(markdown_text):
    for word in markdown_text.split(" "):
        yield word + " "
        time.sleep(0.05)

if 'photo' not in st.session_state:
    st.session_state['photo'] = 'not done'
    
def reset_submission():
    st.session_state['submitted_once'] = False
    st.session_state['photo'] = 'done'

def change_photo_state():
    st.session_state['photo'] = 'done'

camera_file = None
enable = st.checkbox("Enable camera")
if enable:
    camera_file = st.camera_input("Take a picture", label_visibility="collapsed", on_change=change_photo_state, disabled=not enable)
uploaded_file = st.file_uploader("Upload a picture", type=["jpg", "jpeg", "png", "pdf"], label_visibility="collapsed", on_change=change_photo_state)
image_bytes = None
mime_type = None

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded picture", width=300)
    image_bytes = uploaded_file.getvalue()
    mime_type = uploaded_file.type
if camera_file is not None:
    st.image(camera_file, caption="Camera picture")
    image_bytes = camera_file.getvalue()
    mime_type = camera_file.type

prompt_choice = st.radio(
    "Choose a type of note",
    ["Rewrite in a :rainbow[better] way", "Explain all the :red[***complex***] terms" , "I am feeling :green[freaky] :alien:", "Solve :blue[questions] :pencil:"],
    captions=[
        "Note is too boring? Let's make it interesting!",
        "Understand the complex terms and concepts.",
        "Only for big brains.",
        "Get a solution to the questions."
    ],
    on_change=reset_submission
)

if prompt_choice == "Rewrite in a :rainbow[better] way":
    prompt = '''Rewrite the given note into a detailed and well-structured format as if prepared by an A-grade student.
                            Requirements:
                            - Do not include the original note in the response.
                            - Do not write any unncesessary text like "I hope you understand blablabla" at the end.
                            - Do not use any unicode characters that doesn't support latex to pdf conversion like emojis.
                            - Use markdown, keeping sections organized and easy to read.
                            - Add a section that explains complex terms and concepts in simple, everyday language.
                            - Use clear and concise language, avoid unnecessary text and emojis.
                            - Use LaTeX in markdown for math equations.
                            - Format code sections in markdown if they are directly relevant to the note.
                            - Use tables to present data visually if it improves clarity.
                            - Have a seperate section where you Explain like the way you would explain to a 5 year old.
                            - Include additional relevant information that could help a student understand the topic better.
                            - Include a 'Remember' section that highlights key takeaways or important points for easy review.'''
elif prompt_choice == "Explain all the :red[***complex***] terms":
    prompt = '''Provide definitions for complex terms as you would explain to a university-level student familiar with fundamental concepts but seeking a deeper understanding.
                            Requirements:
                            - Table for prerequisite terms (only unique terms required to understand the main terms).
                            - Table for main terms.
                            - Explain using layman's terms while keeping technical accuracy. Prioritize explaining harder terms, especially any that are prerequisites.
                            - Structure the response in markdown with two organized tables:
                                - Limit each definition to 1-2 concise sentences, avoiding redundancy across tables.
                                - Keep it technical yet straightforward—avoid oversimplification and any unnecessary text.
                            - Avoid unsupported characters like emojis for LaTeX-PDF compatibility.
                            '''
elif prompt_choice == "I am feeling :green[freaky] :alien:":
    prompt = '''Imagine you are in a fairy tale or a hilarious movie of complexity. Explain complex terms and concepts in more complex terms that is extreamly hard to understand.
                            Requirements:
                            - Fill the text with full of emojis.
                            - Use markdown.
                            - Always come up with an excuse and make up stuff that is funny but does not make any sense.
                            - Use the topic as a theme and make the note as a story which is gibberish.
                            - Do not let the user know that you are intentionally making the note hard to understand.
                            - Do not use any title like 'Excuse', 'Note', 'Made up Fact
                            - Keep your response short and funny'''
else:
    prompt = '''Provide a detailed solution to the questions/Exercises.
                            Requirements:
                            - Divide the questions/exercises into parts and solve each part separately.
                            - Do not write any unncesessary text like at the end.
                            - Do not use any unicode characters that doesn't support latex to pdf conversion like emojis.
                            - Use markdown, keeping sections organized and easy to read.
                            - Keep the solution clear and concise.
                            - Keep explainations simple and easy to understand.'''

submit = st.button("Cook the notes")
if submit or st.session_state.get('submitted_once', False):
    st.session_state['submitted_once'] = True

    if st.session_state['photo'] == 'done' and image_bytes is not None:
        st.markdown(footer,unsafe_allow_html=True)
        random_message = random.choice(spinner_messages)
        with st.spinner(random_message):
            uploaded_file_obj = None
            temp_file_path = None
            try:
                suffix = mimetypes.guess_extension(mime_type) or '.tmp'
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                    temp_file.write(image_bytes)
                    temp_file_path = temp_file.name

                uploaded_file_obj = genai.upload_file(path=temp_file_path, mime_type=mime_type)

                response = model.generate_content([prompt, uploaded_file_obj], stream=False)
                response.resolve()
                markdown_text = response.text

            except Exception as e:
                st.error(f"An error occurred with the Gemini API: {e}")
                markdown_text = "Error generating response."
            finally:
                if uploaded_file_obj:
                    try:
                       genai.delete_file(uploaded_file_obj.name)
                    except Exception as e:
                       print(f"Error deleting file {uploaded_file_obj.name}: {e}")

                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        if user_api_key:
            st.info("Using user-provided Gemini API key.")
        else:
            st.info("Using default system Gemini API key.")

        st.markdown(markdown_text)

        pdf_response = requests.post(url, data={"markdown": markdown_text, "engine": "pdflatex"})
        output = pdf_response.content

        if pdf_response.status_code != 200:
            pdf_response = requests.post(url, data={"markdown": markdown_text, "engine": "wkhtmltopdf", "css": css})
            output = pdf_response.content

        st.download_button(
            label="Download PDF",
            data=output,
            file_name="output.pdf",
            mime="application/pdf",
        )

        st.session_state['markdown_text'] = markdown_text
        st.session_state['output'] = output
        st.session_state['photo'] = 'not done'
        st.session_state['submitted_once'] = False
        image_bytes = None

    elif image_bytes is None and st.session_state['photo'] == 'done':
        st.warning("Please upload or take a picture first.")
        st.session_state['markdown_text'] = None
        st.session_state['submitted_once'] = False
        st.session_state['output'] = None
        st.session_state['photo'] = 'not done'

    elif st.session_state.get('markdown_text'):
        st.markdown(st.session_state['markdown_text'])
        if st.session_state.get('output'):
             st.download_button(
                label="Download PDF Again",
                data=st.session_state['output'],
                file_name="output.pdf",
                mime="application/pdf",
            )
        st.markdown(footer, unsafe_allow_html=True)
    else:
        st.session_state['markdown_text'] = None
        st.session_state['submitted_once'] = False
        st.session_state['output'] = None

