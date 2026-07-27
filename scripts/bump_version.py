#!/usr/bin/env python3
import re
import os
import sys

repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
notifications_path = os.path.join(repo_dir, "notifications.yaml")

if not os.path.exists(notifications_path):
    print(f"Error: {notifications_path} not found.")
    sys.exit(1)

with open(notifications_path, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r"name:\s*Modern Multi-Device Notifications\s+v(\d+)\.(\d+)", content)
if not match:
    # If no version number found, default to v1.1
    old_version = "unversioned"
    new_version = "v1.1"
    content = re.sub(
        r"(name:\s*Modern Multi-Device Notifications)",
        r"\1 v1.1",
        content
    )
    content = re.sub(
        r"(alias:\s*Modern Multi-Device Notifications)",
        r"\1 v1.1",
        content
    )
else:
    major = int(match.group(1))
    minor = int(match.group(2)) + 1
    old_version = f"v{match.group(1)}.{match.group(2)}"
    new_version = f"v{major}.{minor}"
    content = re.sub(
        r"(name:\s*Modern Multi-Device Notifications\s+)v\d+\.\d+",
        rf"\g<1>{new_version}",
        content
    )
    content = re.sub(
        r"(alias:\s*Modern Multi-Device Notifications\s+)v\d+\.\d+",
        rf"\g<1>{new_version}",
        content
    )

with open(notifications_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Bumped blueprint version: {old_version} -> {new_version}")
