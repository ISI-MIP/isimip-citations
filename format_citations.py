#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path

import pypandoc
import structlog
from jinja2 import Template

logger = structlog.get_logger()

markdown_template = open('template.md').read()

pandoc_template = '''
---
geometry: margin=1in
colored-links: true
linkcolor: blue
urlcolor: orange
...
'''

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', dest='input_file', default='resources.json',  type=Path)
    parser.add_argument('-o', dest='output_path', default='resources.md', type=Path)

    args = parser.parse_args()

    with open(args.input_file) as fp:
        resources = json.load(fp)

    # sort resources by citation count
    resources = sorted([
        resource for resource in resources if resource['citations_count'] > 0
    ], key=lambda r: r['citations_count'], reverse=True)

    # compile a list of publications
    dois = set()
    publications = {}
    for resource in resources:
        for resource in resources:
            for citation in resource['citations']:
                doi = citation.get('doi')

                if doi not in dois:
                    publication_year = citation.get('publication_year')
                    if publication_year in publications:
                        publications[publication_year].append(citation)
                    else:
                        publications[publication_year] = [citation]

                dois.add(doi)

    # sort publications in each year by date
    for year in publications:
        publications[year] = sorted(publications[year], key=lambda r: r['publication_date'], reverse=True)

    # render the markdown template
    rendered_template = Template(markdown_template).render(
        resources=resources,
        publications=publications,
        today=datetime.today().strftime("%B %d, %Y")
    )

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

if __name__ == '__main__':
    main()
