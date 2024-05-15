import os
import difflib
from xml.dom import minidom
from googletrans import Translator

# Original XML file path
original_xml_file = "resource-test.xml"

# List of language codes for translation (replace with desired codes)
languages = [ "de"]  # French

# Create translator object
translator = Translator()

def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def print_changed_lines(old_content, new_content):
    diff = difflib.ndiff(old_content, new_content)
    added_lines = []
    deleted_lines = []

    for line in diff:
        if line.startswith('+ '):
            added_lines.append(line[2:].strip())
        elif line.startswith('- '):
            deleted_lines.append(line[2:].strip())

    if added_lines:
        print("New or modified lines:")
        for line in added_lines:
            print(f"  + {line}")
    if deleted_lines:
        print("Deleted lines:")
        for line in deleted_lines:
            print(f"  - {line}")

def translate_and_update(text_nodes, language_code):
    original_texts = [node.data.strip() for node in text_nodes]
    translations = translator.translate(original_texts, dest=language_code)
    for node, translation in zip(text_nodes, translations):
        node.data = translation.text
    return original_texts, [t.text for t in translations]

def remove_blank_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('\n'.join(lines))
                             

def write_translated_xml(output_file_path, translated_items):
    if not translated_items:
        print("No translated items to append. Keeping the output file unchanged.")
        return
    # Check if the output file already exists
    output_exists = os.path.exists(output_file_path)

    # Create a new XML document or append to an existing one
    if not output_exists:
        output_doc = minidom.Document()
        resource_element = output_doc.createElement("Resource")
        output_doc.appendChild(resource_element)
    else:
        output_doc = minidom.parse(output_file_path)
        resource_element = output_doc.documentElement

    # Append translated items to the resource element
    for name, translation in translated_items:
        item_element = output_doc.createElement("item")
        item_element.setAttribute("name", name)
        item_element.appendChild(output_doc.createTextNode(translation))

        resource_element.appendChild(item_element)

    # Write the output XML document to the specified file path
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(output_doc.toprettyxml(indent="", encoding="utf-8").decode("utf-8"))

    remove_blank_lines(output_file_path)

    print(f"XML translated and {'appended to' if output_exists else 'saved to'} {output_file_path}")

def get_starting_item_index():
    try:
        with open("previous_line_result", "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0  # Start from the beginning if no valid number found

def write_starting_item_index(item_index):
    with open("previous_line_result", "w") as f:
        f.write(str(item_index))

# Open the original XML file for reading
xml_doc = minidom.parse(original_xml_file)

# Get the root element
root = xml_doc.documentElement

# Get starting item index
starting_item_index = get_starting_item_index()

# Loop through each language code
for language_code in languages:
    # Output file path for the current language
    output_folder = f"output_{language_code}"
    output_file_path = f"{output_folder}/{os.path.splitext(original_xml_file)[0]}_{language_code}.xml"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List to store translated item tuples (name, translation)
    translated_items = []

    # Get all "item" elements
    all_items = xml_doc.getElementsByTagName("item")

    # Split the items into chunks to avoid hitting the Google Translate API limit
    chunk_size = 100
    for i in range(starting_item_index, len(all_items), chunk_size):
        chunk = all_items[i:i + chunk_size]
        text_nodes = [item.firstChild for item in chunk if item.firstChild]
        original_texts, translations = translate_and_update(text_nodes, language_code)
        for item, original_text, translation in zip(chunk, original_texts, translations):
            translated_items.append((item.getAttribute("name"), translation))
            print(f"Translated '{original_text}' to '{translation}'")

    # Write translated items to the output XML file
    write_translated_xml(output_file_path, translated_items)

    # Update starting item index for the next run
    write_starting_item_index(len(all_items))

    print(f"XML translated and {'appended to' if starting_item_index > 0 else 'saved to'} {output_file_path} ({language_code})")


    # Monitor the file for changes
content_file_path = 'file_content.txt'
current_content = read_file_content(original_xml_file)

if os.path.exists(content_file_path):
    with open(content_file_path, 'r') as content_file:
        stored_content = [line.strip() for line in content_file.readlines()]
    
    # Compare the current content with the stored content
    if current_content != stored_content:
        print("File has been modified.")
        print_changed_lines(stored_content, current_content)
        
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