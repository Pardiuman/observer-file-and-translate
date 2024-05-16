import os
import difflib
from xml.dom import minidom
from googletrans import Translator
import xml.etree.ElementTree as ET
import subprocess
import time

import xml

original_xml_file = "resource-test.xml"

languages = ["de"]

translator = Translator()

def cleanup_html_entities(translated_text):
    translated_text = translated_text.replace("&gt;", ">")
    translated_text = translated_text.replace("&lt;", "<")
    translated_text = translated_text.replace("&amp;", "&")

    return translated_text

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]
    

def translate_dict(original_dict, language_code):
    translated_dict = {}
    # Translate each value in the original dictionary
    for key, value in original_dict.items():
        retries = 0
        try:
            original_translation = translator.translate(value, dest=language_code)
            translation = cleanup_html_entities(original_translation)
            translated_dict[key] = translation.text
        except Exception as e:
            retries+1
            print(f"Error translating text. Retrying in 5 seconds...\nError: {e}")
            time.sleep(5)
            
    return translated_dict
    
def extract_cdata_value(line):
    # Find the CDATA content within the line
    start_index = line.find('<![CDATA[')
    end_index = line.find(']]>')
    if start_index != -1 and end_index != -1:
        return line[start_index + 9:end_index].strip()
    return ''

def process_changes(old_content, new_content):
    diff = difflib.ndiff(old_content.splitlines(), new_content.splitlines())
    data_dict = {}

    in_cdata_block = False
    current_key = None
    current_cdata_lines = []

    for line in diff:
        if line.startswith('+ '):
            stripped_line = line[2:].strip()

            if not in_cdata_block:
                # Check if this line starts a CDATA block
                if stripped_line.startswith('<![CDATA['):
                    in_cdata_block = True
                    current_cdata_lines.append(stripped_line)
                else:
                    try:
                        root = ET.fromstring(stripped_line)
                        key = root.attrib.get('name', '')
                        value = root.text.strip() if root.text is not None else ''
                        data_dict[key] = value
                    except ET.ParseError as e:
                        print(f"Error parsing line '{stripped_line}': {e}")
            else:
                # Continue collecting lines within the CDATA block
                current_cdata_lines.append(stripped_line)

                # Check if this line ends the CDATA block
                if stripped_line.endswith(']]>'):
                    in_cdata_block = False
                    cdata_value = '\n'.join(current_cdata_lines)
                    data_dict[current_key] = extract_cdata_value(cdata_value)
                    current_cdata_lines = []
        elif in_cdata_block:
            # Continue collecting lines within the CDATA block
            current_cdata_lines.append(line.strip())

    return data_dict

def remove_blank_lines(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]

    with open(file_path, 'w') as file:
        file.write('\n'.join(lines))

def process_output_doc(output_doc_path, data_dict):
  try:
    # Parse the XML document
    doc = minidom.parse(output_doc_path)
    root = doc.documentElement

    # Iterate over each key-value pair in data_dict
    for key, value in data_dict.items():
      found = False
      for item_element in root.getElementsByTagName("item"):
        if item_element.getAttribute("name") == key:
          # Update the text content for any matching element
          item_element.firstChild.data = value
          found = True
          break  # Exit loop after update for a key

      if not found:
        # Create a new element if no match is found
        new_element = doc.createElement("item")
        new_element.setAttribute("name", key)
        new_text_node = doc.createTextNode(value)
        new_element.appendChild(new_text_node)
        root.appendChild(new_element)

    # Serialize the updated XML document and overwrite the original file
    with open(output_doc_path, "w", encoding="utf-8") as output_file:
      output_file.write(doc.toprettyxml(indent="", encoding="utf-8").decode("utf-8"))

    print(f"Updated XML file '{output_doc_path}' with translated values.")
  except FileNotFoundError:
    print(f"Error: File '{output_doc_path}' not found.")
  except Exception as e:
    print(f"Error processing XML file '{output_doc_path}': {e}")



def translate_node(node, dest_lang):
    if node.nodeType == node.TEXT_NODE and node.data.strip():
        translated_text = None
        retries = 0
        while translated_text is None:
            try:
                original_translated = translator.translate(node.data, dest=dest_lang).text
                translated_text = cleanup_html_entities(original_translated)
                print(f"{node.data} translated into :- {translated_text}")
            except Exception as e:
                retries+1
                print(f"Error translating text. Retrying in 5 seconds...\nError: {e}")
                time.sleep(5)
        node.data = translated_text
    for child in node.childNodes:
        translate_node(child,  dest_lang)


file_path = original_xml_file
# Path to the file where we store the previous content
content_file_path = 'file_content.txt'
# Read the current content of the file and normalize it
current_content = read_file_content(file_path)
data_dict_from_difference = {}

if os.path.exists(content_file_path):
    with open(content_file_path, 'r') as content_file:
        stored_content = content_file.readlines()
    
    # Compare the current content with the stored content
    if current_content != stored_content:
        print("File has been modified.")
        data_dict_from_difference = process_changes(stored_content, current_content)
    
        # Update the stored content with the current content
        with open(content_file_path, 'w', encoding='utf-8') as content_file:
            content_file.writelines([line + '\n' for line in current_content])
    else:
        print("No changes detected.")
else:
    # If content file does not exist, create it and store the current content
    with open(content_file_path, 'w',encoding='utf-8') as content_file:
        content_file.writelines([line + '\n' for line in current_content])
    print("Monitoring started. Initial file content:")
    for line in current_content:
        print(line)



for language in languages:
    output_folder = f"output_{language}"
    output_file_path = f"{output_folder}/{os.path.splitext(original_xml_file)[0]}_{language}.xml"

    if os.path.exists(output_folder) and data_dict_from_difference:
        xml_doc = minidom.parse(original_xml_file)
        all_items=xml_doc.getElementsByTagName("item")
        tarnslated_dict = translate_dict(data_dict_from_difference,language)
        print(tarnslated_dict)
        process_output_doc(output_file_path,tarnslated_dict)
        remove_blank_lines(output_file_path)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        xml_doc = minidom.parse(original_xml_file)
        all_items = xml_doc.getElementsByTagName("item")
        translate_node(xml_doc,language)
        # with open(output_file_path, 'w', encoding='utf-8') as file:
        #     output_file_path.write(xml_doc.toprettyxml(file, encoding='utf-8').decode('utf-8'))
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(xml_doc.toprettyxml(indent="", encoding="utf-8").decode("utf-8"))
        remove_blank_lines(output_file_path)
