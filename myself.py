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

def translate_dict(original_dict, language_code):
    translated_dict = {}
    # Translate each value in the original dictionary
    for key, value in original_dict.items():
        retries = 0
        try:
            translation = translator.translate(value,language_code)
            # original_translation = translator.translate(value, dest=language_code)
            # translation = cleanup_html_entities(original_translation).replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
            translated_dict[key] = translation.text
        except Exception as e:
            retries+1
            print(f"Error translating text. Retrying in 5 seconds...\nError: {e}")
            time.sleep(5)
            
    return translated_dict

def read_file_content(file_path):
    with open(file_path, 'r',encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]
    



def print_changed_lines(old_content, new_content):
    diff = difflib.ndiff(old_content, new_content)
    added_lines = []
    data_dict = {}
    for line in diff:
        if line.startswith('+ '):
            striped_line = line[2:].strip()
            if striped_line and not striped_line.startswith('<!--'):
                try:
                    root = ET.fromstring(striped_line)
                    key = root.attrib.get('name', '')
                    value = root.text.strip() if root.text is not None else ''
                    data_dict[key] = value
                except ET.ParseError as e:
                    print(f"Error parsing line '{striped_line}': {e}")
                    continue


    # for line in diff:
    #     if line.startswith('+ '):
    #         striped_line = line[2:].strip()
    #         root = ET.fromstring(striped_line)
    #         key = root.attrib['name']
    #         value = root.text.strip()
    #         data_dict[key]=value
    #         print(data_dict)

    if added_lines:
        print("New or modified lines:")
        for line in added_lines:
            print(line)
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
                translated_text = translator.translate(node.data,dest_lang)
                # original_translated = translator.translate(node.data, dest=dest_lang)
                # translated_text = cleanup_html_entities(original_translated).replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
                # translated_text = cleanup_html_entities(original_translated)
                print(f"{node.data} translated into :- {translated_text}")
            except Exception as e:
                retries+1
                print(f"Error translating text. Retrying in 5 seconds...\nError: {e}")
                time.sleep(5)
        node.data = translated_text.text
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
        stored_content = [line.strip() for line in content_file.readlines()]
    
    # Compare the current content with the stored content
    if current_content != stored_content:
        print("File has been modified.")
        data_dict_from_difference = print_changed_lines(stored_content, current_content)

        
        # Update the stored content with the current content
        with open(content_file_path, 'w') as content_file:
            content_file.writelines([line + '\n' for line in current_content])
    else:
        print("No changes detected.")
else:
    # If content file does not exist, create it and store the current content
    with open(content_file_path, 'w') as content_file:
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
        print(f" {output_file_path} is successfully written down")
        remove_blank_lines(output_file_path)

    #     # Translate and update text nodes in the XML document
    #     original_texts, translations = translate_and_update([item.firstChild for item in all_items if item.firstChild], language)
    #     # Create a list of translated items (name, translated_text)
    #     translated_items = [(item.getAttribute("name"), translation) for item, translation in zip(all_items, translations)]
    #     # Write translated items to the output XML file
    #     write_translated_xml(output_file_path, translated_items)

    # remove_blank_lines(output_file_path)














# def translate_and_update(text_nodes, language_code):
#     original_texts = [node.data.strip() for node in text_nodes]
#     translations = translator.translate(original_texts, dest=language_code)
#     for node, translation in zip(text_nodes, translations):
#         node.data = translation.text
#     return original_texts, [t.text for t in translations]
###############################################################################


# def write_translated_xml(output_file_path, translated_items):
#     output_doc = minidom.Document()
#     resource_element = output_doc.createElement("Resource")
#     output_doc.appendChild(resource_element)
    
#    # Append translated items to the resource element
#     for name, translation in translated_items:
#         item_element = output_doc.createElement("item")
#         item_element.setAttribute("name", name)
#         item_element.appendChild(output_doc.createTextNode(translation))

#         resource_element.appendChild(item_element)

#     # Write the output XML document to the specified file path
#     with open(output_file_path, "w", encoding="utf-8") as output_file:
#         output_file.write(output_doc.toprettyxml(indent="", encoding="utf-8").decode("utf-8"))

#     remove_blank_lines(output_file_path)

#     print(f"'saved to' {output_file_path}")








###################################################### COMMENTED CODE HERE #######################################
######################################  WORKING FINE ##############################################
# def process_output_doc(output_doc_path, data_dict):
#     try:
#         # Parse the XML document
#         doc = minidom.parse(output_doc_path)
#         root = doc.documentElement

#         # Iterate over each key-value pair in data_dict
#         for key, value in data_dict.items():
#             # Find existing elements with matching 'name' attribute
#             matching_elements = root.getElementsByTagName("item")
#             found = False

#             for element in matching_elements:
#                 if element.getAttribute("name") == key:
#                     # Update the text content of the existing element
#                     if element.firstChild and element.firstChild.nodeType == minidom.Node.TEXT_NODE:
#                         element.firstChild.data = value
#                     found = True
#                     break

#             if not found:
#                 # Create a new element for the missing key
#                 new_item_element = doc.createElement("item")
#                 new_item_element.setAttribute("name", key)
#                 new_text_node = doc.createTextNode(value)
#                 new_item_element.appendChild(new_text_node)
#                 root.appendChild(new_item_element)

#         # Serialize the updated XML document and overwrite the original file
#         with open(output_doc_path, "w", encoding="utf-8") as output_file:
#             output_file.write(doc.toprettyxml(indent="", encoding="utf-8").decode("utf-8"))

#         print(f"Updated XML file '{output_doc_path}' with translated values.")
#     except FileNotFoundError:
#         print(f"Error: File '{output_doc_path}' not found.")
#     except Exception as e:
#         print(f"Error processing XML file '{output_doc_path}': {e}")
#####################################################################################################


######################## THIS WORKS BUT WHEN WE ADD A NEW LINE THEN IT IS CREATING A NEW TAG LIKE PARDIUM AND ADRESS NOT NAME
# def process_output_doc(output_doc_path, data_dict):
#   try:
#     # Parse the XML document
#     doc = minidom.parse(output_doc_path)
#     root = doc.documentElement

#     # Iterate over each key-value pair in data_dict
#     for key, value in data_dict.items():
#       # Split the value by newlines to handle multiline data
#       value_lines = value.splitlines()

#       for line in value_lines:
#         found = False

#         # Check for existing element with matching 'name' attribute
#         for item_element in root.getElementsByTagName("item"):
#           if item_element.getAttribute("name") == key:
#             found = True
#             break  # No need to search further for existing element

#         if not found:
#           # Create a new element for each line in the value
#           new_element = doc.createElement("item")
#           new_element.setAttribute("name", key)
#           new_text_node = doc.createTextNode(line)
#           new_element.appendChild(new_text_node)
#           root.appendChild(new_element)

#     # Serialize the updated XML document and overwrite the original file
#     with open(output_doc_path, "w", encoding="utf-8") as output_file:
#       output_file.write(doc.toprettyxml(indent="", encoding="utf-8").decode("utf-8"))

#     print(f"Updated XML file '{output_doc_path}' with translated values.")
#   except FileNotFoundError:
#     print(f"Error: File '{output_doc_path}' not found.")
#   except Exception as e:
#     print(f"Error processing XML file '{output_doc_path}': {e}")
#################################################################################
