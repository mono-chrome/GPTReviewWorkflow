import subprocess
import sys


fetch_result = subprocess.check_output(["git", "fetch", "origin", "main"])
diff_result = str(subprocess.check_output(["git", "diff", f"origin/main"]))
print(diff_result)