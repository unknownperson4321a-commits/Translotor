import streamlit as st
import fitz  # PyMuPDF
from deep_translator import GoogleTranslator
import time

# Page Configuration
st.set_page_config(
    page_title="PDF to English Translator",
    page_icon="🌍",
    layout="centered"
)

st.title("🌍 PDF to English Translator App")
st.markdown(
    "Upload any text-based PDF document (in any language), and this app will "
    "automatically extract its text, translate it into **English**, and let you download the result."
)

st.divider()

# File Uploader component
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Display file details
    file_details = {"FileName": uploaded_file.name, "FileSize": f"{uploaded_file.size / 1024:.2f} KB"}
    st.write("### File Details")
    st.json(file_details)

    if st.button("Translate to English", type="primary"):
        with st.spinner("Extracting and translating text... Please wait."):
            try:
                # Read PDF content via PyMuPDF
                pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                
                extracted_text = ""
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    extracted_text += f"\n--- Page {page_num + 1} ---\n"
                    extracted_text += page.get_text("text")

                if not extracted_text.strip():
                    st.error("No readable text found in this PDF. It might be scanned/image-based.")
                else:
                    # Initialize translator (auto-detect source language, target is English)
                    translator = GoogleTranslator(source='auto', target='en')
                    
                    # Google Translator has a character chunk limit (~4500 characters per request)
                    # We will split text into manageable chunks safely
                    max_chunk_size = 4000
                    text_chunks = [extracted_text[i:i + max_chunk_size] for i in range(0, len(extracted_text), max_chunk_size)]
                    
                    translated_chunks = []
                    progress_bar = st.progress(0)
                    
                    for idx, chunk in enumerate(text_chunks):
                        if chunk.strip():
                            # Translate chunk
                            translated_chunk = translator.translate(chunk)
                            translated_chunks.append(translated_chunk)
                        else:
                            translated_chunks.append("")
                        
                        # Update progress bar
                        progress_bar.progress((idx + 1) / len(text_chunks))
                        time.sleep(0.1) # Gentle pause to prevent rate-limiting

                    final_translated_text = "\n".join(translated_chunks)

                    st.success("Translation completed successfully!")
                    
                    # Display preview
                    st.subheader("Translation Preview")
                    st.text_area("Translated Text", final_translated_text, height=300)

                    # Download button for translated text
                    st.download_button(
                        label="Download Translated Text (.txt)",
                        data=final_translated_text,
                        file_name=f"translated_{uploaded_file.name}.txt",
                        mime="text/plain"
                    )

            except Exception as e:
                st.error(f"An error occurred during processing: {e}")
