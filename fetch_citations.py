#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import requests
import structlog

resources_url = 'https://data.isimip.org/api/v1/resources/?page_size=1000'
datacite_url = 'https://api.datacite.org/dois/'
crossref_url = 'https://api.crossref.org/works/'

datacite_headers = crossref_headers = {
    'User-Agent': 'isimip-citations/1.0 (https://www.isimip.org; mailto:jochen.klar@pik-potsdam.de)'
}

citations = {}
metadata = {}

logger = structlog.get_logger()

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('doi', nargs='*', type=parse_doi, default=None, help='Process only one DOI')
    parser.add_argument('-a', dest='all', action='store_true', help='Process older DOI as well')
    parser.add_argument('-o', dest='output_path', default='resources.json', type=Path)

    args = parser.parse_args()

    resources = fetch_resources(resources_url)

    output_resources = []
    for resource in resources:
        if (args.doi and resource['doi'] in args.doi) or (not args.all and resource.get('new_version')):
            continue

        versions = get_versions(resources, resource)

        resource_citation_dois = set()
        for doi in versions:
            if doi not in citations:
                citations[doi] = fetch_datacite_citations(doi)
            resource_citation_dois.update(citations[doi])

        resource_citations = []
        for doi in resource_citation_dois:
            if doi not in metadata:
                metadata[doi] = fetch_crossref_metadata(doi)
            resource_citations.append(metadata[doi])

        output_resources.append({
            'doi': resource['doi'],
            'doi_url': resource.get('doi_url'),
            'creators_str': resource.get('creators_str'),
            'title': resource.get('title'),
            'publication_date': resource.get('publication_date'),
            'publication_year': resource.get('publication_year'),
            'publisher': resource.get('publisher'),
            'citation': resource.get('citation'),
            'citations': resource_citations
        })

    args.output_path.parent.mkdir(exist_ok=True, parents=True)
    with open(args.output_path, 'w') as fp:
        json.dump(output_resources, fp, indent=2, ensure_ascii=False)


def fetch_resources(url):
    logger.info('querying isimip-data', url=url)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    if data['next']:
        return data['results'] + fetch_resources(data['next'])
    else:
        return data['results']


def get_versions(resources, resource, versions=[]):
    previous_version = resource.get('previous_version')
    if previous_version:
        try:
            previous_resource = next(r for r in resources if r['doi'] == previous_version)
            return [resource['doi'], *get_versions(resources, previous_resource, versions)]
        except StopIteration:
            pass

    return [resource['doi']]


def parse_doi(string):
    match = re.search(r'10\.\d{5}\/ISIMIP\.\d{6}\.*\d*$', string)
    if match:
        return match.group(0)


def fetch_datacite_citations(doi):
    url = datacite_url + doi
    logger.info('querying datacite', url=url)
    datacite_response = requests.get(url, headers=datacite_headers)
    datacite_response.raise_for_status()
    datacite_data = datacite_response.json().get('data', {})

    datacite_related_identifiers = {
        related_identifier.get('relatedIdentifier') for related_identifier in
        datacite_data.get('attributes', {}).get('relatedIdentifiers', [])
    }

    datacite_citations = {
        citation.get('id') for citation in
        datacite_data.get('relationships', {}).get('citations', {}).get('data', [])
    }

    return (datacite_citations - datacite_related_identifiers)


def fetch_crossref_metadata(doi):
    url = crossref_url + doi
    logger.info('querying crossref', url=url)
    try:
        crossref_response = requests.get(crossref_url + doi, headers=crossref_headers)
        crossref_response.raise_for_status()
        crossref_data = crossref_response.json().get('message', {})
    except requests.exceptions.HTTPError:
        logger.error('error with crossref api', doi=doi, status=crossref_response.status_code)
        return None

    doi_url = f'https://doi.org/{doi}'
    timestamp = crossref_data.get('created', {}).get('timestamp')
    publication_date = str(datetime.fromtimestamp(timestamp / 1e3).date()) if timestamp else None
    publication_year = str(datetime.fromtimestamp(timestamp / 1e3).year) if timestamp else None
    creators_str = ', '.join([
        '{given} {family}'.format(**author)
        for author in crossref_data.get('author', [])
    ])
    title = crossref_data.get('title')[0]
    publisher = crossref_data.get('publisher')

    return {
        'doi': doi,
        'doi_url': doi_url,
        'creators_str': creators_str,
        'title': title,
        'publication_date': publication_date,
        'publication_year': publication_year,
        'publisher': publisher,
        'citation': f'{creators_str} ({publication_year}): {title}. {publisher}. {doi_url}'
    }


if __name__ == '__main__':
    main()
