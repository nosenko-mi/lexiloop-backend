import sys
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from os.path import splitext, isdir, isfile, join
from os import listdir


def load_book(path) -> epub.EpubBook:
    return epub.read_epub(path)


def get_parapraphs(book)-> list[str]:
    items = []

    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        if "main" in item.get_name():
            items.append(item.get_content().decode("utf-8").replace('\n', ' '))

    chapters = []
    for i in items:
        soup = BeautifulSoup(i, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = ' '.join(chunk for chunk in chunks if chunk)
        chapters.append(text)
    
    return chapters


def write_to_file(list):
    pass


def save_file(path, data):
    _, ext = splitext(path)

    if (ext == None):
        path += '.txt'

    with open(path, 'w', encoding='utf-8') as file:
        for c in data:
            file.write('<chapter>')
            file.write(c)
            # file.write('</chapter>')


# def main():
#     if len(sys.argv) < 3:
#         print("Not all arguments were provided.")
#         print(sys.argv[0] + ": <source_path> <destination_path> ")
#         sys.exit(1)

#     source_path = sys.argv[1]
#     destination_path = sys.argv[2]
    
#     if isdir(source_path) and isdir(destination_path):
#         files = [f for f in listdir(source_path) if isfile(join(source_path, f))]
#         for f in files:
#             source = join(source_path, f)
#             d, _ = splitext(join(destination_path, f))
#             destination = d + ".txt"
#             book = load_book(source)
#             paragraphs = get_parapraphs(book)
#             save_file(destination, paragraphs)
#     elif isfile(source_path) and isfile(destination_path):
#         book = load_book(source_path)
#         paragraphs = get_parapraphs(book)
#         save_file(destination_path, paragraphs)
#     else: 
#         print(f"Unsupported configuration. Use either:\n{sys.argv[0]}: <source_dir> <destination_dir>\n{sys.argv[0]}: <source_file> <destination_file> ")
#         sys.exit(1)


# main()

# python parse.py ./books/the-wonderful-wizard-of-oz.epub ./parsed/the-wonderful-wizard-of-oz.txt
# or
# python parse.py ./books ./parsed
