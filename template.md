# ISIMIP data citations

{{ today }}

| Dataset                                                           | No. of Citations |
| ----------------------------------------------------------------- | ---------------- |{% for resource in resources %}
| {{ resource.title_with_version }} | {{ resource.citations_count }} |{% endfor %}

## Dataset citations

{% for resource in resources %}
### {{ resource.title_with_version }}

DOI: <{{ resource.doi_url }}>

Citations: {{ resource.citations_count }}

{% for citation in resource.citations %}* {{ citation.creators_str }} ({{ citation.publication_year }}): **{{ citation.title }}**. {% if citation.journal %}{{ citation.journal }}{% else %}{{ citation.publisher }}{% endif %}. <{{ citation.doi_url}}>
{% endfor %}
{% endfor %}


## Citing publications by year

{% for year, publication_list in publications.items() %}
### {{ year }}

{% for publication in publication_list %}* {{ publication.creators_str }} ({{ publication.publication_year }}): **{{ publication.title }}**. {% if publication.journal %}{{ publication.journal }}{% else %}{{ publication.publisher }}{% endif %}. <{{ publication.doi_url}}>.
{% endfor %}{% endfor %}
