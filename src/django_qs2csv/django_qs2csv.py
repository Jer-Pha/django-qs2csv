from django.http import HttpResponse
from django.db.models import QuerySet

SYMBOLS = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]


def error_handler(
    qs: QuerySet,
    values: bool,
    filename: str,
) -> None:
    """
    Documentation needed.
    """
    # Ensure `values` is only being used with a QuerySet with .values()
    if values and not issubclass(qs[0].__class__, dict):
        raise TypeError(
            "`values=True` only works with a QuerySet that utilizes .values()."
            " QuerySets for model objects or values_list() are not compatible."
        )

    # Ensure `filename` is properly formatted
    filename = filename.strip()
    if filename != "export":
        if len(filename) > 251 or not filename:
            raise ValueError(
                "`filename` must be between 1 and 251 characters. Current"
                f" length is {len(filename)}."
            )
        elif [i for i in SYMBOLS if i in filename]:
            raise ValueError(
                "`filename` can not contain these characters:"
                f" {' '.join(SYMBOLS)}"
            )
        elif filename[-1] == ".":
            raise ValueError(f"`filename` can not end in a period.")

    # Check if the QuerySet has been evaluated:
    if qs._result_cache is not None:
        from warnings import warn
        warning = (
            "The QuerySet was already evaluated before being passed to this"
            " function. This will result in another database hit converting"
            " the QuerySet to a list of dicts by using values()."
        )
        if qs and not values and issubclass(qs[0].__class__, dict):
            warning += (
                "\nTo avoid this, pass `values=True` as a parameter. This will"
                " use the QuerySet as-is. Note: `values` overrides the `only`"
                " and `defer` params, which means fields must be filtered"
                " before the QuerySet is passed to this function.\nThis can"
                " only be done if you are using values()."
            )
        warn(warning, ResourceWarning)


def get_fields(
    fields: list[object],
    only: list[str],
    defer: list[str],
) -> list[str]:
    """
    Documentation needed.
    """
    if only:
        # `defer` overrides `only`
        only = [f for f in only if f not in defer]
        fields = [f for f in fields if f.name in only]
    elif defer:
        fields = [f for f in fields if f.name not in defer]

    # Remove unsupported fields and convert to list of strings
    return [
        f.name for f in fields if f.get_internal_type() != "ManyToManyField"
    ]


def queryset_to_csv(
    qs: QuerySet,
    header: bool = True,
    values: bool = False,
    pd: bool = False,
    only: list[str] = [],
    defer: list[str] = [],
    filename: str = "export",
) -> HttpResponse:
    """
    Documentation needed.

    `headers` includes Content-Type and Content-Disposition. To add
    headers, set the new header as an index key and assign a value to
    it. e.g. `response = queryset_to_csv(qs)` ->
    `response['Custom-Header'] = "This is my customer header."
    To delete a content-header, use `del`, such as:
    `response = queryset_to_csv(qs)` -> `del response['Content-Type']`

    OneToOneField and ForeignKey fields will show the connected model's
    primary key, not the __str__ value. This is a limitation of using
    values().
    """
    # Check for errors
    error_handler(qs, values, filename)

    # Specify which fields need to be used with values()
    fields = get_fields(qs.model._meta.local_fields, only, defer)

    # Convert QuerySet to list of dicts
    if not values:
        qs = qs.values(*fields)

    # Create the response
    response = HttpResponse(
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": f"attachment; filename={filename}.csv",
        },
    )

    # Build csv file
    if pd:
        from pandas import DataFrame
        DataFrame(qs).to_csv(response, header=header, index=False)
    else:
        from csv import DictWriter
        list(qs)  # Force evaluation to prevent multiple queries
        #                                 vvvvvvvvvvvv
        csv_writer = DictWriter(response, qs[0].keys())
        if header:
            csv_writer.writeheader()
        csv_writer.writerows(qs)

    return response
