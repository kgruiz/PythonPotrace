from pathlib import *

ignore = ["./Tests", "./Docs", "./Examples", "pyproject.toml", "temp.py"]

ignore = [Path(path).resolve() for path in ignore]

currentDir = Path(".").resolve()

with Path("out.txt").open("w") as file:

    for item in currentDir.rglob("*.py"):

        if not any(parent in ignore for parent in [item] + list(item.parents)) and "__init__.py" != item.name:

            file.write(f"# {item.relative_to(currentDir)}\n\n")

            with item.open("r") as sourceFile:

                file.write(sourceFile.read() + "\n\n")
