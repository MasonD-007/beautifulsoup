import os


def parser_for(path):
    return "xml" if path.lower().endswith((".xml", ".dtd")) else "html.parser"


def output_path(path, task):
    stem = os.path.splitext(os.path.basename(path))[0]
    ext = os.path.splitext(path)[1] or ".html"
    return f"{stem}_{task}{ext}"
