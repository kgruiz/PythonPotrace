import re
from pathlib import Path

mdFile = Path("Docs/COutline.md").resolve()

content = mdFile.read_text()

headerPattern = r"^(#{1,2} .*)"

matches = re.findall(headerPattern, content, flags=re.MULTILINE)

for match in matches:

    print(match)
