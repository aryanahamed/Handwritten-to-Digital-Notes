import os
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

if 'photo' not in st.session_state:
    st.session_state['photo'] = 'not done'
    
def change_photo_state():
    st.session_state['photo'] = 'done'


st.title("Better Notes 📝", anchor=False)
st.caption("Upload a picture of your notes or take one. One file at a time.")

camera_file = st.camera_input("or take a picture", label_visibility="collapsed", on_change=change_photo_state)
uploaded_file = st.file_uploader("Upload a picture", type=["jpg", "jpeg", "png"], label_visibility="collapsed", on_change=change_photo_state) 

base64_image = None

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded picture")
    base64_image = base64.b64encode(uploaded_file.read()).decode('utf-8')
if camera_file is not None:
    st.image(camera_file, caption="Camera picture")
    base64_image = base64.b64encode(camera_file.read()).decode('utf-8')

if st.session_state['photo'] == 'done' and base64_image is not None:
    completion = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[
            {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": '''Explain the note and write as a new note in a way an A student would take notes.
                                Requirements:
                                1. Output in markdown format.
                                2. Make it enjoyable and introduce a simple game to learn it better Ex. Quick quiz, Memory game, Practice problem, Fill-in-the-blanks exercise, etc. 
                                3. Have a seperate section for explaining it in laymen's term as well as any word that may be confusing for a student. 
                                4. Don't say anything additional after you are done with the notes. 
                                5. Keep it clean and simple. 
                                6. Use emojis if appropriate.
                                7. If you need to output math use latex in markdown to output equations
                                8. If you need to output code use code format in markdown.
                                9. Try using a table in markdown format whenever possible to visualize data better.
                                10. Make sure not to miss anything in the given notes picture.
                                11. Decline to output if the picture is not related to studies.
                                12. Don't Output/Show code if it is not related to the notes.
                                13. Keep a Remember section for the most important points.'''
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
            temperature=0.4,
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
    
    st.session_state['photo'] = 'not done'