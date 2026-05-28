import ast
import os
import sys

FILES = [
    "lambda_function.py",
    "test_local.py"
]

print("\nChecking Python syntax...\n")

all_ok = True

for file in FILES:

    if not os.path.exists(file):
        print(f"[FAIL] Missing file: {file}")
        all_ok = False
        continue

    try:
        with open(file, "r", encoding="utf-8") as f:
            ast.parse(f.read())

        print(f"[OK] {file}")

    except SyntaxError as e:
        print(f"[FAIL] {file}")
        print(f"       {e}")
        all_ok = False

print("\nChecking environment variables...\n")

required_env_vars = [
    "CLOUDINARY_CLOUD_NAME",
    "CLOUDINARY_API_KEY",
    "CLOUDINARY_API_SECRET"
]

for env_var in required_env_vars:

    if os.getenv(env_var):
        print(f"[OK] {env_var}")
    else:
        print(f"[WARN] {env_var} not set")

print("\nChecking project files...\n")

required_files = [
    "lambda_function.py",
    "serverless.yml",
    "requirements.txt",
    "README.md"
]

for file in required_files:

    if os.path.exists(file):
        print(f"[OK] {file}")
    else:
        print(f"[FAIL] Missing {file}")
        all_ok = False

print("\nValidation Complete\n")

if all_ok:
    print("All checks passed. Ready to deploy.")
    sys.exit(0)
else:
    print("Validation failed.")
    sys.exit(1)