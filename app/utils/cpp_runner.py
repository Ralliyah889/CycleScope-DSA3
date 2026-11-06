"""
C++ Runner Utility
Communicates with the compiled C++ Dependency Analyzer executable via subprocess.
"""

import os
import subprocess
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Tuple

# Path to project root and binary
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BINARY_PATH = PROJECT_ROOT / "bin" / "dependency_analyzer"


def ensure_binary_compiled() -> bool:
    """Checks if C++ binary exists; if not, triggers 'make all'."""
    if BINARY_PATH.exists():
        return True

    try:
        res = subprocess.run(
            ["make", "all"],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
        return res.returncode == 0 and BINARY_PATH.exists()
    except Exception as e:
        print(f"Error compiling C++ binary: {e}")
        return False


def run_analyzer(csv_path_or_content: str, is_content: bool = False) -> Tuple[bool, Dict[str, Any], str]:
    """
    Executes the C++ analyzer on a CSV file path or raw CSV content string.
    
    Returns:
        (success: bool, result_dict: dict, error_message: str)
    """
    if not ensure_binary_compiled():
        return False, {}, "C++ binary could not be found or compiled. Please run 'make all' first."

    temp_file_created = False
    csv_file = csv_path_or_content

    if is_content:
        # Write content to temporary CSV file
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tf:
                tf.write(csv_path_or_content)
                csv_file = tf.name
                temp_file_created = True
        except Exception as e:
            return False, {}, f"Failed to create temporary file: {str(e)}"

    try:
        res = subprocess.run(
            [str(BINARY_PATH), str(csv_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15
        )

        stdout = res.stdout.strip()
        stderr = res.stderr.strip()

        if res.returncode != 0:
            # Check if C++ printed a JSON error
            error_text = stderr or stdout or f"Process exited with code {res.returncode}"
            try:
                err_json = json.loads(stdout or stderr)
                if "message" in err_json:
                    error_text = err_json["message"]
            except Exception:
                pass
            return False, {}, f"C++ Analyzer Error: {error_text}"

        try:
            data = json.loads(stdout)
            return True, data, ""
        except json.JSONDecodeError as je:
            return False, {}, f"Failed to parse C++ JSON output: {str(je)}\nOutput: {stdout[:300]}"

    except subprocess.TimeoutExpired:
        return False, {}, "C++ Analyzer timed out after 15 seconds."
    except Exception as e:
        return False, {}, f"Execution failed: {str(e)}"
    finally:
        if temp_file_created and os.path.exists(csv_file):
            try:
                os.remove(csv_file)
            except OSError:
                pass
