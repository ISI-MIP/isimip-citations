#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import pypandoc
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

    resources = sorted([
        resource for resource in resources if resource['citations_count'] > 0
    ], key=lambda r: r['citations_count'], reverse=True)

    rendered_template = Template(markdown_template).render(resources=resources)

    if args.output_path.suffix == '.md':
        args.output_path.write_text(rendered_template)
    elif args.output_path.suffix == '.pdf':
        pypandoc.convert_text(
            pandoc_template + rendered_template,
            'pdf',
            format='markdown',
            outputfile=args.output_path,
            extra_args=['--pdf-engine=xelatex']
        )

markdown_template = '''# ISIMIP data citations
{% for resource in resources %}
## {{ resource.title_with_version }}

DOI: <{{ resource.doi_url }}>

Citations: {{ resource.citations_count }}

{% for citation in resource.citations %}* {{ citation.creators_str }} ({{ citation.publication_year }}): **{{ citation.title }}**. {% if citation.journal %}{{ citation.journal }}{% else %}{{ citation.publisher }}{% endif %}. <{{ citation.doi_url}}>
{% endfor %}
{% endfor %}
'''  # noqa: E501

pandoc_template = '''
---
geometry: margin=1in
colored-links: true
linkcolor: blue
urlcolor: orange
...
'''

if __name__ == '__main__':
    main()
