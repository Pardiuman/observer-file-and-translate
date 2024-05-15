# import os
# import difflib

# # Function to read the content of the file and normalize it
# def read_file_content(file_path):
#     with open(file_path, 'r') as file:
#         return [line.strip() for line in file.readlines()]

# # Function to print added and removed lines
# def print_differences(old_content, new_content):
#     diff = difflib.ndiff(old_content, new_content)
#     added_lines = []
#     removed_lines = []

#     for line in diff:
#         if line.startswith('+ '):
#             added_lines.append(line[2:].strip())
#         elif line.startswith('- '):
#             removed_lines.append(line[2:].strip())

#     if added_lines:
#         print("Added lines:")
#         for line in added_lines:
#             print(line)

#     if removed_lines:
#         print("Removed lines:")
#         for line in removed_lines:
#             print(line)

# # Path to the file to monitor
# file_path = 'test'

# # Path to the file where we store the previous content
# content_file_path = 'file_content.txt'

# # Read the current content of the file and normalize it
# current_content = read_file_content(file_path)

# # Check if the content file exists
# if os.path.exists(content_file_path):
#     with open(content_file_path, 'r') as content_file:
#         stored_content = content_file.readlines()
#     stored_content = [line.strip() for line in stored_content]
    
#     # Compare the current content with the stored content
#     if current_content != stored_content:
#         print("File has been modified.")
#         print_differences(stored_content, current_content)
        
#         # Update the stored content with the current content
#         with open(content_file_path, 'w') as content_file:
#             content_file.writelines([line + '\n' for line in current_content])
#     else:
#         print("No changes detected.")
# else:
#     # If content file does not exist, create it and store the current content
#     with open(content_file_path, 'w') as content_file:
#         content_file.writelines([line + '\n' for line in current_content])
#     print("Monitoring started. Initial file content:")
#     for line in current_content:
#         print(line)



#######################################################################################################


# import os
# import difflib

# # Function to read the content of the file and normalize it
# def read_file_content(file_path):
#     with open(file_path, 'r') as file:
#         return [line.strip() for line in file.readlines()]

# # Function to print added and modified lines
# def print_added_lines(old_content, new_content):
#     diff = difflib.ndiff(old_content, new_content)
#     added_lines = []

#     for line in diff:
#         if line.startswith('+ '):
#             added_lines.append(line[2:].strip())

#     if added_lines:
#         print("New or modified lines:")
#         for line in added_lines:
#             print(line)

# # Path to the file to monitor
# file_path = 'test'

# # Path to the file where we store the previous content
# content_file_path = 'file_content.txt'

# # Read the current content of the file and normalize it
# current_content = read_file_content(file_path)

# # Check if the content file exists
# if os.path.exists(content_file_path):
#     with open(content_file_path, 'r') as content_file:
#         stored_content = content_file.readlines()
#     stored_content = [line.strip() for line in stored_content]
    
#     # Compare the current content with the stored content
#     if current_content != stored_content:
#         print("File has been modified.")
#         print_added_lines(stored_content, current_content)
        
#         # Update the stored content with the current content
#         with open(content_file_path, 'w') as content_file:
#             content_file.writelines([line + '\n' for line in current_content])
#     else:
#         print("No changes detected.")
# else:
#     # If content file does not exist, create it and store the current content
#     with open(content_file_path, 'w') as content_file:
#         content_file.writelines([line + '\n' for line in current_content])
#     print("Monitoring started. Initial file content:")
#     for line in current_content:
#         print(line)

# this working fine

######################################################################################



import os
import difflib

# Function to read the content of the file and normalize it
def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Function to print added and modified lines
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

# Path to the file to monitor
file_path = 'resource-test.xml'

# Path to the file where we store the previous content
content_file_path = 'file_content.txt'

# Read the current content of the file and normalize it
current_content = read_file_content(file_path)

# Check if the content file exists
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
