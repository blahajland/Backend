import ast
import os
import glob

def analyze_directory(directory_path):
    """
    Analyzes all Python files in a directory for function definition and call mismatches.

    Args:
        directory (str): The path to the directory containing the Python files.
    """

    # Get all Python files in the directory
    python_files = glob.glob(os.path.join(directory_to_analyze, "*.py"))

    # Create a dictionary to store function definitions
    function_definitions = {}

    # Analyze each file for function definitions
    for file_path in python_files:
        with open(file_path, "r") as file:
            try:
                tree = ast.parse(file.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        function_name = node.name
                        arguments = [arg.arg for arg in node.args.args]
                        function_definitions[function_name] = {
                            "file": file_path,
                            "arguments": arguments,
                        }
            except SyntaxError as e:
                print(f"Syntax error in file {file_path}: {e}")

    # Analyze each file for function calls and compare with definitions
    for file_path in python_files:
        with open(file_path, "r") as file:
            try:
                tree = ast.parse(file.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        called_function = node.func
                        if isinstance(called_function, ast.Name):
                            called_function_name = called_function.id
                            if called_function_name in function_definitions:
                                # Check if the number of arguments matches
                                call_arguments = len(node.args)
                                definition_arguments = len(
                                    function_definitions[called_function_name]["arguments"]
                                )
                                if call_arguments != definition_arguments:
                                    print(
                                        f"Function call mismatch in {file_path}: "
                                        f"Function '{called_function_name}' "
                                        f"called with {call_arguments} arguments, "
                                        f"but defined with {definition_arguments} in "
                                        f"{function_definitions[called_function_name]['file']}"
                                    )
                            else:
                                print(
                                    f"Warning in {file_path}: "
                                    f"Function '{called_function_name}' not defined in any file."
                                )
            except SyntaxError as e:
                print(f"Syntax error in file {file_path}: {e}")


if __name__ == "__main__":
    directory_to_analyze = "/home/eryn/backendssplit"  # Replace with your directory
    analyze_directory(directory_to_analyze)
