import os
import time
import streamlit as st
from groq import Groq
import base64
import markdown
from xhtml2pdf import pisa
from io import BytesIO
from dotenv import load_dotenv
import requests


load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

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
    <img src='https://groq.com/wp-content/uploads/2024/03/PBG-mark1-color.svg' alt='Powered by Groq for fast inference.' width='50' height='50'/>
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

def change_photo_state():
    st.session_state['photo'] = 'done'


st.title("Better Notes 📝", anchor=False)
st.caption("Upload a picture of your notes or take one. One image at a time.")
st.caption("Try multiple times if the output is not as expected.")
enable = st.checkbox("Enable camera")
camera_file = st.camera_input("or take a picture", label_visibility="collapsed", on_change=change_photo_state, disabled=not enable)
uploaded_file = st.file_uploader("Upload a picture", type=["jpg", "jpeg", "png"], label_visibility="collapsed", on_change=change_photo_state) 
base64_image = None

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded picture", width=300)
    base64_image = base64.b64encode(uploaded_file.read()).decode('utf-8')
if camera_file is not None:
    st.image(camera_file, caption="Camera picture")
    base64_image = base64.b64encode(camera_file.read()).decode('utf-8')

prompt_choice = st.radio(
    "Choose a type of note",
    ["Rewrite in a :rainbow[better] way", "Explain all the :red[***complex***] terms" , "I am feeling :green[freaky] :alien: "],
    captions=[
        "Note is too boring? Let's make it interesting!",
        "Understand the complex terms and concepts.",
        "Let's see what happens.",
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
                            - Explain like the way you would explain to a 5 year old.
                            - Include additional relevant information that could help a student understand the topic better.
                            - Include a 'Remember' section that highlights key takeaways or important points for easy review.'''
elif prompt_choice == "Explain all the :red[***complex***] terms":
    prompt = '''I want you to act as a teacher who explains complex terms and only complex terms in laymen terms but still keeping the technical accuracy.
                            Requirements: 
                            - Do not write any unncesessary text like "I hope you understand blablabla" at the end.
                            - Do not use any unicode characters that doesn't support latex to pdf conversion like emojis.
                            - Use markdown, keeping sections organized and easy to read.
                            - Explain pre-requisite subterms within subterms before explaining the main term. 
                                Example: If you have to explain "Regression", you should explain "Correlation, linearity, multivariable, etc" first.'''
else:
    prompt = '''Imagine you are in a fairy tale or a hilarious movie of complexity. Explain complex terms and concepts in more complex terms that is extreamly hard to understand.
                            Requirements: 
                            - Fill the text with full of emojis.
                            - Use markdown.
                            - Always come up with an excuse and make up stuff that is funny but does not make any sense.
                            - Use the topic as a theme and make the note as a story which is gibberish.
                            - Do not let the user know that you are intentionally making the note hard to understand.
                            - Do not use any title like 'Excuse', 'Note', 'Made up Fact
                            - Keep your response short and funny'''

    
submit = st.button("Cook the notes")
if submit or st.session_state.get('submitted_once', False):
    st.session_state['submitted_once'] = True
    
    if st.session_state['photo'] == 'done' and base64_image is not None and submit:
        st.markdown(footer,unsafe_allow_html=True)

        progress_text = "Cooking the notes... 🍳"
        my_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100):
            time.sleep(0.02)
            my_bar.progress(percent_complete + 1, text=progress_text)
        time.sleep(1)
        my_bar.empty()
        
        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                }
                            },
                        ]
                    },
                    {
                        "role": "assistant",
                        "content": ""
                    }
                ],
                temperature=0.3,
                max_tokens=3072,
                top_p=0.95,
                stream=False,
                stop=None,
            )
        
        markdown_text = completion.choices[0].message.content
        st.write_stream(stream_data(markdown_text))

        response = requests.post(url, data={"markdown": markdown_text, "engine": "pdflatex"})
        output = response.content
        
        if response.status_code != 200:
            response = requests.post(url, data={"markdown": markdown_text, "engine": "wkhtmltopdf", "css": css})
            output = response.content
        
        st.subheader("Please upload the image again to use a different note output.", anchor=False)
        st.download_button(
            label="Download",
            data=output,
            file_name="output.pdf",
            mime="application/pdf",
        )
        
        st.session_state['markdown_text'] = completion.choices[0].message.content
        st.session_state['output'] = output
        st.session_state['photo'] = 'not done'
        st.session_state['submitted_once'] = False
        
    elif base64_image is None:
        st.session_state['markdown_text'] = None
        st.session_state['submitted_once'] = False
        st.session_state['output'] = None
    
    else:
        st.markdown(st.session_state['markdown_text'])
        response = requests.post(url, data={"markdown": st.session_state['markdown_text'], "engine": "pdflatex"})
        output = response.content
        if response.status_code != 200:
            response = requests.post(url, data={"markdown": st.session_state['markdown_text'], "engine": "wkhtmltopdf", "css": css})
            output = response.content
        st.download_button(
            label="Download",
            data=output,
            file_name="output.pdf",
            mime="application/pdf",
        )
        st.markdown(footer, unsafe_allow_html=True)
        if st.session_state.get('photo') == 'not done':
            st.session_state['submitted_once'] = False
        
