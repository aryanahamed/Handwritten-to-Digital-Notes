import os
import time
import streamlit as st
from groq import Groq
import base64
from dotenv import load_dotenv
import requests


load_dotenv()

st.title("Better Notes 📝", anchor=False)
st.caption("Upload a picture of your notes or take one. Choosing the wrong type will result in bad output.")
user_api_key = st.text_input("Enter your API Key (leave blank to use default and please don't abuse)", type="password")
if user_api_key:
    api_key = user_api_key

else:
    api_key = os.environ.get("GROQ_API_KEY")

client = Groq(
    api_key=api_key,
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
    st.session_state['photo'] = 'done'

def change_photo_state():
    st.session_state['photo'] = 'done'

camera_file = None
enable = st.checkbox("Enable camera")
if enable:
    camera_file = st.camera_input("Take a picture", label_visibility="collapsed", on_change=change_photo_state, disabled=not enable)
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
    
    if st.session_state['photo'] == 'done' and base64_image is not None:
        st.markdown(footer,unsafe_allow_html=True)
        with st.spinner("Cooking the notes... 🍳"):
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
                    temperature=1,
                    max_tokens=3072,
                    top_p=0.95,
                    stream=False,
                    stop=None,
                )
        if user_api_key:
            st.info("Using user-provided API key.")
        else:
            st.info("Using default system API key.")
        markdown_text = completion.choices[0].message.content
        st.write_stream(stream_data(markdown_text))

        response = requests.post(url, data={"markdown": markdown_text, "engine": "pdflatex"})
        output = response.content
        
        if response.status_code != 200:
            response = requests.post(url, data={"markdown": markdown_text, "engine": "wkhtmltopdf", "css": css})
            output = response.content
        
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
        base64_image = None
        
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
        st.session_state['submitted_once'] = False
        
