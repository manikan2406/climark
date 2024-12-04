import argparse
import os
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
#import markdown

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# LangChain setup
template = """Instructions: {question}
Generate a detailed markdown document summarizing the Python project structure.
Answer with a markdown document."""
prompt = ChatPromptTemplate.from_template(template)
model = OllamaLLM(model="qwen2.5-coder")
chain = prompt | model
logger.info("LangChain model setup completed.")

def process_project(folder_path):
    """
    Traverse the folder structure and generate markdown documentation.
    """
    logger.debug(f"Scanning folder structure at: {folder_path}")
    project_summary = []
    for root, _, files in os.walk(folder_path):
        relative_root = os.path.relpath(root, folder_path)
        project_summary.append(f"## Directory: {relative_root}\n")
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".py"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                    logger.info(f"Read file: {file_path}")
                    file_doc = generate_markdown_document(code, file, relative_root)
                    project_summary.append(file_doc)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")

    markdown_content = "\n".join(project_summary)
    save_markdown_document(markdown_content, folder_path)

def generate_markdown_document(code, file_name, relative_root):
    """
    Generate markdown documentation for the given Python file using LangChain and Ollama LLM.
    """
    logger.debug("Generating markdown document...")
    question = f"Generate markdown documentation for the following Python file: {file_name}\n\n{code}"
    try:
        response = chain.invoke({"question": question})
        logger.info(f"Markdown document generated for {file_name}.")
        return f"### {file_name}\n\n{clean_code(response)}\n"
    except Exception as e:
        logger.error(f"Error generating markdown document: {e}")
        return f"Error: {e}"

def clean_code(text):
    """
    Clean up the response text to remove unwanted content.
    """
    logger.debug("Cleaning up generated content...")
    lines = text.splitlines()
    return "\n".join(line for line in lines if line.strip() not in ['```python', '```'])

def save_markdown_document(markdown_content, project_path):
    """
    Save the generated markdown document to the project root.
    """
    markdown_folder = os.path.join(project_path, "docs")
    os.makedirs(markdown_folder, exist_ok=True)
    markdown_file_path = os.path.join(markdown_folder, "project_documentation.md")
    try:
        with open(markdown_file_path, "w", encoding="utf-8") as markdown_file:
            markdown_file.write(markdown_content)
        logger.info(f"Markdown document saved to {markdown_file_path}")
    except Exception as e:
        logger.error(f"Error saving markdown document: {e}")

def generate_docs_cli(project_path):
    if not os.path.exists(project_path):
        logger.error(f"Path {project_path} does not exist.")
        return
    try:
        process_project(project_path)
        logger.info("Markdown documentation generated and saved in the docs folder.")
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="CLI tool for generating markdown documentation using Ollama."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate Docs Command
    generate_parser = subparsers.add_parser(
        "generate-docs", help="Generate markdown documentation for a project"
    )
    generate_parser.add_argument("project_path", help="Path to the project folder")

    args = parser.parse_args()

    if args.command == "generate-docs":
        generate_docs_cli(args.project_path)
    else:
        parser.print_help()

