import os
import time
import streamlit as st
from groq import Groq
import base64
import markdown
from xhtml2pdf import pisa
from io import BytesIO

def convert_markdown_to_html(markdown_text):
    html = markdown.markdown(
        markdown_text,
        extensions=['tables', 'fenced_code', 'codehilite']
    )
    
    full_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Roboto, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            code {{ background-color: #f5f5f5; padding: 2px 4px; border-radius: 4px; }}
            pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 4px; }}
        </style>
        <script type="text/x-mathjax-config">
            MathJax.Hub.Config({{
                tex2jax: {{inlineMath: [['$','$'], ['\\\\(','\\\\)']],
                        processEscapes: true}}
            }});
        </script>
        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    return full_html

def convert_html_to_pdf(html_text):
    output = BytesIO()
    # Convert HTML to PDF
    pisa.CreatePDF(
        html_text,
        dest=output,
        encoding='utf-8'
    )
    output_pdf = output.getvalue()
    output.close()
    return output_pdf

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

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

if 'photo' not in st.session_state:
    st.session_state['photo'] = 'not done'
    
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

if st.session_state['photo'] == 'done' and base64_image is not None:
    st.markdown(footer,unsafe_allow_html=True)

    progress_text = "Cooking the notes..."
    my_bar = st.progress(0, text=progress_text)

    for percent_complete in range(100):
        time.sleep(0.03)
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
                            "text": '''Rewrite the given note into a detailed and well-structured format as if prepared by an A-grade student.
                            Requirements:
                            - Output format: Use markdown, keeping sections organized and easy to read.
                            - Simple Explanation: Add a section that explains complex terms and concepts in simple, everyday language.
                            - Explaination for more stupid brains: Explain like the way you would explain to a 5 year old.
                            - Clean Presentation: Use clear and concise language, avoid unnecessary text at the end, and introduce emojis on titles.
                            - Formatting:
                                - Use LaTeX in markdown for math equations.
                                - Format code sections in markdown if they are directly relevant to the note.
                                - Use tables to present data visually if it improves clarity.
                            - Completeness: Make sure all essential points from the original note are covered without adding unrelated information. Don't write anything else after finishing the note.
                            - Extra Information: Include additional relevant information that could help a student understand the topic better.
                            - Summary Section: Include a 'Remember' section that highlights key takeaways or important points for easy review.''',
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
            top_p=1,
            stream=False,
            stop=None,
        )
    
    st.markdown(completion.choices[0].message.content)    
    markdown_text = completion.choices[0].message.content   

    html_text = convert_markdown_to_html(markdown_text)
    output = convert_html_to_pdf(html_text)
    

    st.download_button(
        label="Download",
        data=output,
        file_name="output.pdf",
        mime="application/pdf",
    )
    
    st.caption("Download is still under Alpha. May not work as expected.")
    st.session_state['markdown_text'] = completion.choices[0].message.content
    st.session_state['photo'] = 'not done'

elif 'markdown_text' in st.session_state:
    st.markdown(st.session_state['markdown_text'])
    st.markdown(footer,unsafe_allow_html=True)


