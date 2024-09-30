import streamlit as st
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator
from io import BytesIO
import time  # Import time module to measure duration
from functions import footer, link, image

st.set_page_config(page_title="XperTranslate")
html_temp = """
                    <div style="background-color:{};padding:1px">
                    
                    </div>
                    """



hide="""
<style>
footer{
	visibility: hidden;
    	position: relative;
}
.viewerBadge_container__1QSob{
    visibility: hidden;
}
.viewerBadge_link__1S137{
    visibility: hidden;
}
#MainMenu{
	visibility: hidden;
}
<style>
"""
st.markdown(hide, unsafe_allow_html=True)



st.markdown("<h1 style='text-align: center'><span style='color: #8dc32f'>Xper</span>Translate for <a href='https://xper3.fr/en/' style='color: #8dc32f; text-decoration: none'>Xper3</a></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center'> Importer votre base de connaissances <a href='https://xper3.fr/en/' style='color: #8dc32f; text-decoration: none;font-weight: bold;'>Xper3</a> pour traduction. </p>", unsafe_allow_html=True)

footer()


st.markdown(
    """
    <style>
        iframe[width="220"] {
            position: fixed;
            bottom: 60px;
            right: 40px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

language_choices = {'Français': 'fr', 'Anglais': 'en', 'Espagnol': 'es'}
col1, col2 = st.columns(2)
with col1:
    source_language = st.selectbox('Langue source', list(language_choices.keys()))
with col2:
    translation_language = st.selectbox('Langue de traduction:', list(language_choices.keys()), index=None, placeholder="Choisir la langue de traduction")

if source_language and translation_language and source_language != translation_language:
    # Set up the translator for French to English
    translator = GoogleTranslator(source=language_choices[source_language], target=language_choices[translation_language])
else:
    st.warning("Choisissez une langue de traduction différente de la langue source")
# Function to translate text within a specific tag and update progress
def translate_text(root, tag_name, progress_bar, progress_step):
    tags = root.findall(f".//{tag_name}")
    total_tags = len(tags)

    for i, tag in enumerate(tags):
        original_text = tag.text
        if original_text:
            try:
                translated_text = translator.translate(original_text)
                tag.text = translated_text
            except Exception as e:
                st.error(f"Erreur de traduction {tag_name}: {e}")

        # Update progress
        progress_bar.progress(progress_step * (i + 1) / total_tags)

# Function to process the uploaded XML file and handle progress
def process_xml(file):
    try:
        tree = ET.parse(file)
        root = tree.getroot()

        # Create a progress bar
        progress_bar = st.progress(0)
        total_steps = 2  # Number of translation steps (for Detail and Label)

        # Start measuring time
        start_time = time.time()  # Record the start time

        # Translate texts inside <Detail> and <Label> tags with progress update
        translate_text(root, 'Detail', progress_bar, 0.5)
        translate_text(root, 'Label', progress_bar, 1)

        # Calculate the translation time
        translation_time = time.time() - start_time  # Calculate duration

        # Write updated XML to a string buffer
        buffer = BytesIO()
        tree.write(buffer, encoding='UTF-8', xml_declaration=True)

        # Mark progress complete
        progress_bar.progress(1.0)

        return buffer.getvalue(), translation_time  # Return both XML and translation time
    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier XML: {e}")
        return None, None  # Return None for both in case of error

# Function to format the translation time
def format_translation_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes} minute(s) et {seconds} second(es)" if minutes > 0 else f"{seconds} seconde(s)"

# Streamlit App Interface
# st.title("XperTranslate")
# st.write("Importer votre base de connaissances xper3 pour traduction (du français vers l'anglais).")

# File upload
msg = ""
st.markdown("""
        <style>
            .stButton > button {
                width: 100%;  /* Full width */
                height: 40px; /* Adjust height */
                background-color: #8dc32f; /* Button color */
                color: white; /* Text color */
                border: none; /* Remove border */
                border-radius: 5px; /* Rounded corners */
                font-size: 16px; /* Font size */
            }
            .stButton > button:hover {
                background-color: #fff; /* Darker color on hover */
                border: 1px 0 #8dc32f;
                color: #8dc32f;
            }
        </style>
    """, unsafe_allow_html=True)
with st.sidebar:
    
    st.markdown("""
    # A propos
    """)
    st.markdown("<p>Importer votre base de connaissances <a href='https://xper3.fr/en/' style='color: #8dc32f; text-decoration: none;font-weight: bold;'>Xper3</a> pour la traduction. </p>", unsafe_allow_html=True)
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choisissez une base de connaissances (XML)", type="xml")
    
    # Add a button to trigger the translation
    if uploaded_file is not None:
        if st.button("Traduire"):
            # Process the file and translate content only when the button is clicked
            msg = "Translated"

      
if msg: 
    translated_xml, translation_time = process_xml(uploaded_file)
    if translated_xml:
        # Provide download link for the translated XML
        # Format and display translation time
        formatted_time = format_translation_time(translation_time)
        msg = "Base de connaissances traduite avec succès ("+formatted_time+") !"
        # msg    
        st.write(msg)
        # Create a download button
        st.download_button(
            label="Télécharger la base traduite",
            data=translated_xml,
            file_name="translated_output.xml",
            mime="text/xml"
        )

           
