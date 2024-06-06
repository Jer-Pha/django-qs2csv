from django.http import HttpResponse
from django.db.models import QuerySet


def error_handler(
    qs: QuerySet,
    values: bool,
    filename: str,
) -> None:
    """Checks for errors/warnings in `queryset_to_csv`."""
    # Ensure `values` is only being used with a QuerySet with .values()
    if values and not issubclass(qs[0].__class__, dict):
        raise TypeError(
            "`values=True` only works with a QuerySet that utilizes .values()."
            " QuerySets for model objects or values_list() are not compatible."
        )

    # Ensure `filename` is properly formatted
    filename = filename.strip()
    if filename != "export":
        SYMBOLS = ("<", ">", ":", '"', "/", "\\", "|", "?", "*")

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
    verbose: bool,
) -> list[list[str]]:
    """Determines which fields to include in the response."""
    # Remove ManyToManyField (unsupported)
    if only:
        # `defer` overrides `only`
        only = [f for f in only if f not in defer]
        fields = [f for f in fields if f.name in only and not f.many_to_many]
    elif defer:
        fields = [
            f for f in fields if f.name not in defer and not f.many_to_many
        ]
    else:
        fields = [f for f in fields if not f.many_to_many]

    # Convert fields to field name strings
    return (
        (
            [f.name for f in fields],
            [f.verbose_name for f in fields],
        )
        if verbose
        else ([f.name for f in fields],)
    )


def queryset_to_csv(
    qs: QuerySet,
    header: bool = False,
    filename: str = "export.csv",
    only: list[str] = [],
    defer: list[str] = [],
    verbose: bool = True,
    values: bool = False,
    pd: bool = False,
) -> HttpResponse:
    """Converts a QuerySet into a CSV file as an HttpResponse.

    This function takes a Django QuerySet and converts it into a CSV
    file through a django.http.HttpResponse object. The function can
    take several ``Parameters`` that will affect the exported data.

    Parameters
    ----------
    qs
        The QuerySet that will be converted to a CSV file.
    header : default=False
        Add/remove a header row of field names in the response.
    filename : default="export.csv"
        The file name for the exported file. Does not need .csv suffix.
    only : default=[]
        List of specific fields to include in the response.
    defer : default=[]
        List of specific fields not to include in the response

    Returns
    -------
    HttpResponse
        Includes the Content-Type and Content-Disposition headers.

    Other Parameters
    ----------
    verbose : default=True
        Use the verbose_name from the selected fields.
    values : default=False
        Use the QuerySet as-is, must use values(). See ``Notes``.
    pd : default=False
        Use pandas.DataFrame().to_csv() instead of csv.DictWriter().


    Raises
    ------
    ValueError
        If `filename` is not formatted correctly.
    TypeError
        If `values=True` and the QuerySet did not call values().

    Warns
    -----
    ResourceWarning
        If the QuerySet will be evaluated more than once.

    See Also
    --------
    error_handler : Checks for errors/warnings in this function.
    get_fields : Determines which fields to include in the response.

    Notes
    -----
    ForeignKey and OneToOneField will always return the primary key,
    because the function uses values().

    ManyToManyField is not supported.

    `headers` includes Content-Type and Content-Disposition. To add
    headers, set the new header as an index key and assign a value to
    it, the same as a dictionary. These headers can also be deleted
    (not recommended).

    If the QuerySet was already evaluated before being passed to the
    function then it will be re-evaluated. Depending on the size of the
    QuerySet and the database setup, this may add a noticeable delay.
    It is recommended to monitor the impact of database queries using
    django.db.connection.queries or django-debug-toolbar during
    development. If the QuerySet must be evaluated before the function
    is called, it would be most efficient to use values() with the
    QuerySet (if possible) then pass `values=True`.

    If your QuerySet uses only() / defer() then you must include those
    same fields in the `only` / `defer` parameters when calling the
    function. The function transforms all QuerySets into a list of
    dicts w/ values(), which is incompatible with only() and defer().
    """
    # Check for errors
    error_handler(qs, values, filename)

    # Specify the fields for values() and the header row
    fields = get_fields(qs.model._meta.local_fields, only, defer, verbose)
    headers = fields[-1] if header else []
    fields = fields[0]

    # Convert QuerySet to list of dicts
    if not values:
        qs = qs.values(*fields)

    # Check if the filename already includes the correct file type
    if filename[-4:] != ".csv":
        filename += ".csv"

    # Create the response
    response = HttpResponse(
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": f"attachment; filename={filename}",
        },
    )

    # Build csv file
    if not pd:
        from csv import DictWriter

        csv_writer = DictWriter(response, fields)
        if header and verbose:
            csv_writer.writerow(dict(zip(fields, headers)))
        elif header:
            csv_writer.writeheader()
        csv_writer.writerows(qs)
    else:
        from pandas import DataFrame

        if header and verbose:
            from csv import writer

            csv_writer = writer(response)
            csv_writer.writerow(headers)
            DataFrame(qs).to_csv(response, header=False, index=False, mode="a")
        else:
            DataFrame(qs).to_csv(response, header=header, index=False)

    return response
