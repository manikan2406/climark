import argparse
import os
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
import subprocess

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# LangChain setup
template = """Instructions: {question}
Generate maximum test cases possible for the above code. Make sure you have done the necessary imports as all the files will be outside the tests folder. Strictly give only final code as output. Don't give things other than python code in output.
Answer: ."""
prompt = ChatPromptTemplate.from_template(template)
model = OllamaLLM(model="qwen2.5-coder")
chain = prompt | model
logger.info("LangChain model setup completed.")

def process_project(folder_path):
    """
    Traverse the folder structure, generate test cases for each Python file, and save them.
    """
    logger.debug(f"Scanning folder structure at: {folder_path}")
    for root, _, files in os.walk(folder_path):
        relative_root = os.path.relpath(root, folder_path)
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".py"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                    logger.info(f"Read file: {file_path}")
                    test_code = generate_test_cases(code, file)
                    save_test_cases(file, test_code, folder_path)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")

def generate_test_cases(code, file_name):
    """
    Generate pytest cases for the given code using LangChain and Ollama LLM.
    """
    logger.debug("Generating test cases...")
    question = f"Generate pytest cases for the following Python file: {file_name}\n\n{code}"
    try:
        response = chain.invoke({"question": question})
        logger.info("Test cases generated successfully.")
        return clean_code(response)
    except Exception as e:
        logger.error(f"Error generating test cases: {e}")
        return f"Error: {e}"

def clean_code(text):
    """
    Remove markdown code block markers (```python and ```) from the text.
    """
    logger.debug("Cleaning up code block markers...")
    lines = text.splitlines()
    return "\n".join(line for line in lines if line.strip() not in ['```python', '```'])

def save_test_cases(file_name, test_code, project_path):
    """
    Save the generated test cases to the tests folder.
    """
    tests_folder = os.path.join(project_path, "tests")
    os.makedirs(tests_folder, exist_ok=True)
    test_file_name = f"test_{os.path.splitext(file_name)[0]}.py"
    test_file_path = os.path.join(tests_folder, test_file_name)
    try:
        with open(test_file_path, "w", encoding="utf-8") as test_file:
            test_file.write(test_code)
        logger.info(f"Test cases saved to {test_file_path}")
    except Exception as e:
        logger.error(f"Error saving test cases for {file_name}: {e}")

def create_pytest_ini_with_llm(tests_folder):
    """
    Create a pytest.ini file with basic configurations using LLM.
    """
    logger.info("Creating pytest.ini using LLM...")
    template = """Generate a pytest.ini file with the following configurations:
    1. testpaths: The folder where the tests are located (tests).
    2. addopts: Verbose output (-v).
    3. markers: Define smoke and regression markers.
    4. Enable log capturing with level INFO and format 'asctime - levelname - message'.
    """
    try:
        response = chain.invoke({"question": template})
        pytest_ini_content = clean_code(response)
        pytest_ini_path = os.path.join(tests_folder, "pytest.ini")
        with open(pytest_ini_path, "w", encoding="utf-8") as pytest_ini_file:
            pytest_ini_file.write(pytest_ini_content)
        logger.info(f"pytest.ini saved to {pytest_ini_path}")
    except Exception as e:
        logger.error(f"Error creating pytest.ini: {e}")

def validate_tests(test_folder):
    """
    Run pytest on the specified folder and return the results.
    """
    logger.debug(f"Running pytest for folder: {test_folder}")
    result = subprocess.run(["pytest", test_folder], capture_output=True, text=True)
    logger.info("Pytest execution completed.")
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }

def generate_tests_cli(project_path):
    if not os.path.exists(project_path):
        logger.error(f"Path {project_path} does not exist.")
        return
    try:
        process_project(project_path)
        create_pytest_ini_with_llm(os.path.join(project_path, "tests"))
        logger.info("Test cases generated and saved in the tests folder.")
    except Exception as e:
        logger.error(f"Error generating tests: {e}")

def validate_tests_cli(project_path):
    tests_path = os.path.join(project_path, "tests")
    if not os.path.exists(tests_path):
        logger.error(f"Tests folder {tests_path} does not exist.")
        return
    try:
        validation_result = validate_tests(tests_path)
        print("Validation Results:")
        print(validation_result["stdout"])
        if validation_result["stderr"]:
            print("\nErrors:")
            print(validation_result["stderr"])
    except Exception as e:
        logger.error(f"Error validating tests: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="CLI tool for generating and validating test cases using Ollama."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate Tests Command
    generate_parser = subparsers.add_parser(
        "generate-tests", help="Generate test cases for a project"
    )
    generate_parser.add_argument("project_path", help="Path to the project folder")

    # Validate Tests Command
    validate_parser = subparsers.add_parser(
        "validate-tests", help="Validate test cases for a project"
    )
    validate_parser.add_argument("project_path", help="Path to the project folder")

    args = parser.parse_args()

    if args.command == "generate-tests":
        generate_tests_cli(args.project_path)
    elif args.command == "validate-tests":
        validate_tests_cli(args.project_path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
