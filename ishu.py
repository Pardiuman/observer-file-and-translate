from xml.dom import minidom
from googletrans import Translator
from collections import defaultdict

import os
import time


# Original XML file path
original_xml_file = "resource-test.xml"

# List of language codes for translation
#languages = ["de", "en", "es", "fr", "it", "ko", "pt", "tr", "zh-CN"]
languages = ["de", "fr", "it"]

# Batch size for translation
batch_size = 100  # Adjust this value as needed

# Create translator object
translator = Translator()

def load_translations(xml_file, language_code):
    """
    Load already translated lines from the existing translated XML file.
    """
    translations = {}
    if os.path.exists(output_file_path):
        translated_doc = minidom.parse(output_file_path)
        text_nodes = translated_doc.getElementsByTagName("item")
        for node in text_nodes:
            key = node.getAttribute("id")
            value = node.firstChild.data.strip()
            translations[key] = value
    return translations

def translate_batch(text_list, language_code):
    """
    Translates a list of text strings in a single request.
    """
    while True:
        try:
            translations = translator.translate(text_list, dest=language_code)
         
            return [translation.text for translation in translations]
        except Exception as e:
            print(f"Translation failed due to error: {e}")
            print("Retrying translation after 5 seconds...")
            time.sleep(5)

# Open the original XML file for reading
xml_doc = minidom.parse(original_xml_file)

# Get the root element
root = xml_doc.documentElement

# Loop through each language code
for language_code in languages:

    output_folder = f"output_{language_code}"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Generate output file path within the language folder
    
    output_file_path = f"{output_folder}/{os.path.splitext(original_xml_file)[0]}_{language_code}.xml"
    # Load already translated lines
    translated_lines = load_translations(output_file_path, language_code)

    # Create a copy of the original XML document for each language
    translated_doc = xml_doc.cloneNode(deep=True)

    # Get all text nodes to translate
    text_nodes = [item for item in translated_doc.getElementsByTagName("item")]

    # Batch translation
    batch_text = []
    for node in text_nodes:
        key = node.getAttribute("id")
        if key not in translated_lines:
            text = node.firstChild.data.strip() if node.firstChild else ""
            batch_text.append(text)

    for i in range(0, len(batch_text), batch_size):
        print(f"Translating batch {i // batch_size + 1} out of {len(batch_text) // batch_size + 1} batches...")
        
        # Retry translation up to 3 times
        retry_count = 0
        while retry_count < 3:
            try:
                translations = translate_batch(batch_text[i:i + batch_size], language_code)
                print(f"Translated {len(translations)} texts in this batch.")
                break  # Break the retry loop if translation succeeds
            except Exception as e:
                retry_count += 1
                print(f"Translation failed due to error: {e}")
                if retry_count < 3:
                    print(f"Retrying translation ({retry_count}/3) after 5 seconds...")
                    time.sleep(5)
                else:
                    print("Translation failed after multiple retries. Skipping this batch.")
                    break

        # Update text nodes with translations
        for j, translation in enumerate(translations):
            key = text_nodes[i + j].getAttribute("id")
            if key not in translated_lines and text_nodes[i + j].firstChild:
                text_nodes[i + j].firstChild.data = translation

    # Generate output folder path with language code as folder name
    

    # Write the translated XML data to a separate file
    with open(output_file_path, "w", encoding="utf-8") as f:
        translated_doc.writexml(f, indent="  ", encoding="utf-8")

    print(f"XML translated and written to {output_file_path} ({language_code})")