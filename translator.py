"""Translates pseudocode into python code."""
def main_thread(lines):
    """Main thread handling most of the logic."""
    output = ""

    for line in lines:
        print(line)
        continue

    return output

def main():
    """Main function, reads and writes files."""
    in_file = open("in.txt", 'r', encoding="UTF8")
    out_file = open("out.py", 'w', encoding="UTF8")

    all_lines = []
    for line in in_file:
        line += all_lines
    output_text = main_thread(all_lines)

    out_file.write(output_text)
    in_file.close()
    out_file.close()

main()
