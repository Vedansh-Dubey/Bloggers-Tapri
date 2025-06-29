import re

import re
import base64
import os
from datetime import datetime
from typing import Dict, Optional


def clean_tag_output(raw_output: str) -> str:
    lines = re.split(r"[\n,]+", raw_output)
    tags = [tag.strip().lower().replace(" ", "-") for tag in lines if tag.strip()]
    tags = [
        re.sub(r"[^a-z0-9\-]", "", tag) for tag in tags
    ]
    return ",".join(tags)


def get_credibility_badge(credibility: str) -> str:
    cred_class = {
        "High": "high-cred",
        "Medium": "med-cred",
        "Low": "low-cred",
        "User Provided": "user-cred",
    }.get(credibility, "med-cred")
    return f'<span class="credibility-badge {cred_class}">{credibility}</span>'


def image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def parse_references(markdown_content: str) -> Dict[str, str]:
    references = {}
    ref_pattern = r"\[\^(\d+)\]: (.+?)(?=\n\[\^\d+\]: |\Z)"
    for match in re.finditer(ref_pattern, markdown_content, re.DOTALL):
        ref_id = match.group(1)
        ref_content = match.group(2).strip()
        references[ref_id] = ref_content
    return references


def clean_tag(tag: str) -> str:
    return tag.lower().replace("-", "").replace(" ", "")


def calculate_duration(start_time: datetime) -> float:
    return (datetime.now() - start_time).total_seconds()
