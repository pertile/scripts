# Open the SQL file in read mode
with open(r"c:\temp\2ndfloor_vbulletin.2024.07.02.sql", "r", encoding="latin-1") as file:
    # Initialize an empty list to hold the lines that start with "CREATE TABLE"
    create_table_lines = []
    
    # Loop through each line in the file
    for line in file:
        # Check if the line starts with "CREATE TABLE"
        if line.strip().upper().startswith("CREATE TABLE"):
            # If it does, add the line to the list
            create_table_lines.append(line)

# Optional: Write the extracted lines to a new file
with open(r"c:\temp\create_table_lines.sql", "w", encoding="utf-8") as output_file:
    # Write each line in the list to the file
    for line in create_table_lines:
        output_file.write(line)

# Print a message indicating completion
print("Extraction complete. Check c:\\temp\\create_table_lines.sql for the results.")