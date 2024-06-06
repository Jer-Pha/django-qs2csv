# django-qs2csv

A simple package to convert a Django QuerySet to a CSV file through an HttpResponse object.

## Getting started

### Prerequisites

* Python >= 3.8
* Django >= 3.2

### Optional Dependencies

* pandas >= 1.5

### Installation

Recommended
```console
pip install django-qs2csv
```

Full
```console
pip install django-qs2csv[pd]
```
Note: this will install [pandas](https://pandas.pydata.org/), which is used with ``queryset_to_csv_pd()``. It is not recommended to install the pandas library unless you will use this function or already use pandas. Using ``queryset_to_csv_pd()`` will likely increase the export speed of large QuerySets (2M+ results) and decrease file size for all QuerySets.

## Usage

views.py

```shell
from django_qs2csv import qs_to_csv

from .models import SampleModel

...

def export_csv(request):
    ...

    my_queryset = SampleModel.objects.all()

    response = qs_to_csv(
        my_queryset,
        filename="all_sample_models",
    )

    return response
```

### Return type

`qs_to_csv` returns a `django.http.HttpResponse` with the `Content-Type` and `Content-Disposition` headers. Additional headers can be added to the response before returning:

```shell
...

response = qs_to_csv(my_queryset)
response["Another-Header"] = "This is another header for the HttpResponse."

...
```

### Parameters

`qs : QuerySet` - The QuerySet to be exported as a CSV file. This can be passed as QuerySet\[object], QuerySet\[dict] (values()), or QuerySet\[list\[list]] (values_list()). See the note in the [Limitations](#limitations) about QuerySet evaluation. **Required**

`header : bool` - Include a header row with field names. **Default: False**

`filename : str` - The name of the exported CSV file. You do not need to include .csv, it will be added once the filename is evaluated. File names can not end in a period, include the symbols (< > : " / \\ | ? *), or be longer than 251 characters (255 w/ ".csv"). **Default: "export"**

`only : list[str]` - List the field names that you would like to include in the exported file. An empty list will include all fields, other than those in `defer`. Field names listed in both `only` and `defer` will not be included. See the note in the [Limitations](#limitations) section for details how this works with a QuerySet that calls only() / defer(). **Default: []**

`defer : list[str]` - List the field names that you do not want to include in the exported file. An empty list will include all fields, or just those mentioned in `only`. Field names listed in both `only` and `defer` will not be included. See the note in the [Limitations](#limitations) section for details how this works with a QuerySet that calls only() / defer(). **Default: []**

`verbose : bool` - Determine if the header row uses the fields' `verbose_name` or just the field names. This only applies when `header=True`. **Default: True**

`values : bool` - Only enable this if your QuerySet was already evaluated (no longer lazy) and called values(). You must ensure your fields are properly selected in the original QuerySet, because this will skip applying the `only` and `defer` parameters. **Default: False**

### Limitations

If the QuerySet was already evaluated before being passed to `qs_to_csv` then it will be re-evaluated by the function. Depending on the size of the QuerySet and the database setup, this may add a noticeable delay. It is recommended to monitor the impact of database queries using `django.db.connection.queries` or [django-debug-toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/index.html) during development. If the QuerySet must be evaluated before the function is called, it would be most efficient to use values() with the QuerySet (if possible) then pass `values=True` to `qs_to_csv`.

If your QuerySet uses only() / defer() then you must include those same fields in the `only` / `defer` parameters when calling `qs_to_csv`. The function transforms all QuerySets into a list of dicts using values(), which is incompatible with only() and defer().

`ForeignKey` and `OneToOneField` will always return the primary key, because the function uses `values()`.

`ManyToManyField` is not supported.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
