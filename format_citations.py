#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import structlog
from jinja2 import Template

logger = structlog.get_logger()

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', dest='input_file', default='resources.json',  type=Path)
    parser.add_argument('-o', dest='output_path', default='resources.md', type=Path)

    args = parser.parse_args()

    with open(args.input_file) as fp:
        resources = json.load(fp)

    resources = [
        dict(**resource, count=len(resource['citations']))
        for resource in resources if len(resource['citations']) > 0
    ]

    resources = sorted(resources, key=lambda r: r['count'], reverse=True)

    if args.output_path.suffix == '.md':
        args.output_path.write_text(Template(markdown_template).render(resources=resources).strip())


markdown_template = '''
# ISIMIP citations

{% for resource in resources %}## {{ resource.title }}

DOI: {{ resource.doi }}

Citations: {{ resource.count }}

{% for citation in resource.citations %}* {{ citation.citation }}
{% endfor %}
{% endfor %}

'''

if __name__ == '__main__':
    main()
