from typing import Any, Dict, List, Optional, Tuple, Union

from django.http import HttpResponse
from django.db.models import QuerySet


def validate_filename(filename: str) -> str:
    """Ensures `filename` is properly formatted."""
    # Only process `filename` if it is not the default value.
    if filename != "export.csv":
        SYMBOLS = ("<", ">", ":", '"', "/", "\\", "|", "?", "*")
        filename = filename.strip()

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

    if filename[-4:] != ".csv":
        filename += ".csv"

    return filename


def create_response(filename: str) -> HttpResponse:
    """Creates HttpResponse with necessary headers."""
    return HttpResponse(
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": (
                f"attachment; filename={validate_filename(filename)}"
            ),
        },
    )


def set_fields(
    fields: List[object],
    only: List[str],
    defer: List[str],
) -> List[object]:
    """Determines which fields to include in the response.

    Removes ManyToManyField (unsupported) and applies `only` and
    `defer` filters then returns a list of field objects.

    """
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

    return fields


def get_fields(
    fields: List[object],
    header: bool,
    verbose: bool,
) -> Tuple[List[str], Optional[List[str]]]:
    """Gets header then converts fields to a list of strings."""
    if header and verbose:
        headers = [f.verbose_name for f in fields]
    elif header:
        headers = [f.name for f in fields]
    else:
        headers = None

    return [f.name for f in fields], headers


def qs_to_csv_core(
    qs: Union[
        QuerySet[object],
        QuerySet[Dict[Any, Any]],
        QuerySet[List[Any]],
    ],
    filename: str,
    only: List[Optional[str]],
    defer: List[Optional[str]],
) -> Tuple[HttpResponse, List[object]]:
    """Core functionality of all package functions."""
    fields = set_fields(qs.model._meta.local_fields, only, defer)
    return create_response(filename), fields


def qs_to_values(
    qs: Union[
        QuerySet[object],
        QuerySet[Dict[Any, Any]],
        QuerySet[List[Any]],
    ],
    filename: str,
    only: List[Optional[str]],
    defer: List[Optional[str]],
    header: bool,
    verbose: bool,
    values: bool,
    pd: bool = False,
) -> Tuple[
    QuerySet[Dict[Any, Any]],
    HttpResponse,
    List[str],
    Optional[List[str]],
]:
    """Converts QuerySet to a list of dicts using values()."""
    response, fields = qs_to_csv_core(qs, filename, only, defer)
    fields, headers = get_fields(fields, header, verbose)

    if not values:
        qs = qs.values(*fields)
    elif not issubclass(qs[0].__class__, dict):
        raise TypeError(
            "``values=True`` only works with a QuerySet that utilizes"
            " .values(). QuerySets for model objects or values_list()"
            " are not compatible."
        )

    return (
        (qs, response, headers, fields) if not pd else (qs, response, headers)
    )


def qs_to_csv(
    qs: Union[QuerySet[object], QuerySet[Dict[Any, Any]], QuerySet[List[Any]]],
    filename: str = "export.csv",
    only: List[str] = [],
    defer: List[str] = [],
    header: bool = False,
    verbose: bool = True,
    values: bool = False,
) -> HttpResponse:
    """Converts a QuerySet into a CSV file as an HttpResponse.

    This function takes a Django QuerySet and converts it into a CSV
    file through a django.http.HttpResponse object. The function can
    take several ``Parameters`` that will affect the exported data.

    Parameters
    ----------
    qs
        The QuerySet that will be converted to a CSV file.
    filename : default="export.csv"
        The file name for the exported file. Does not need .csv suffix.
    only : default=[]
        List of specific fields to include in the response.
    defer : default=[]
        List of specific fields not to include in the response
    header : default=False
        Add/remove a header row of field names in the response.

    Returns
    -------
    HttpResponse
        Includes the "Content-Type" and "Content-Disposition" headers.

    Other Parameters
    ----------
    verbose : default=True
        Use the verbose_name from the selected fields.
    values : default=False
        Use the QuerySet as-is, must use values(). See ``Notes``.

    See Also
    --------
    qs_to_csv_pd()
    qs_to_csv_rel_str()

    Raises
    ------
    ValueError
        If `filename` is not formatted correctly.
    TypeError
        If ``values=True`` and the QuerySet did not call values().

    Notes
    -----
    ForeignKey and OneToOneField will always return the primary key,
    because the function uses values().

    ManyToManyField is not supported.

    The returned HttpResponse includes headers Content-Type and
    Content-Disposition. To add headers, set the new header as an index
    key and assign a value to it, the same as a dictionary. These
    headers can also be deleted (not recommended).

    If the QuerySet was already evaluated before being passed to the
    function then it will be re-evaluated. Depending on the size of the
    QuerySet and the database setup, this may add a noticeable delay.
    It is recommended to monitor the impact of database queries using
    django.db.connection.queries or django-debug-toolbar during
    development. If the QuerySet must be evaluated before the function
    is called, it would be most efficient to use values() with the
    QuerySet (if possible) then pass ``values=True``.

    If your QuerySet uses only() / defer() then you must include those
    same fields in the `only` / `defer` parameters when calling the
    function. The function transforms all QuerySets into a list of
    dicts w/ values(), which is incompatible with only() and defer().
    This also applies if you specify fields in values() or values_list().

    """
    qs, response, headers, fields = qs_to_values(
        qs, filename, only, defer, header, verbose, values
    )

    # Build csv file
    from csv import DictWriter

    csv_writer = DictWriter(response, fields)
    if header and verbose:
        csv_writer.writerow(dict(zip(fields, headers)))
    elif header:
        csv_writer.writeheader()
    csv_writer.writerows(qs)

    return response


def qs_to_csv_pd(
    qs: Union[QuerySet[object], QuerySet[Dict[Any, Any]], QuerySet[List[Any]]],
    filename: str = "export.csv",
    only: List[str] = [],
    defer: List[str] = [],
    header: bool = False,
    verbose: bool = True,
    values: bool = False,
) -> HttpResponse:
    """This is a copy of qs_to_csv() that uses the pandas library.

    This function is identical to qs_to_csv() except that it uses
    pandas.DataFrame().to_csv() instead of csv.DictWriter().

    Dependencies
    ------------
    pandas >= 1.5

    See Also
    --------
    qs_to_csv

    """
    qs, response, headers = qs_to_values(
        qs, filename, only, defer, header, verbose, values, pd=True
    )

    # Build csv file
    from pandas import DataFrame

    if header and verbose:
        from csv import writer

        csv_writer = writer(response)
        csv_writer.writerow(headers)
        DataFrame(qs).to_csv(response, header=False, index=False, mode="a")
    else:
        DataFrame(qs).to_csv(response, header=header, index=False)

    return response


def qs_to_csv_rel_str(
    qs: Union[QuerySet[object], QuerySet[Dict[Any, Any]], QuerySet[List[Any]]],
    filename: str = "export.csv",
    only: List[str] = [],
    defer: List[str] = [],
    header: bool = False,
    verbose: bool = True,
    values: bool = False,
) -> HttpResponse:
    """This is a copy of qs_to_csv() that prints __string__ for related
    fields ForeignKey and OneToOneField instead of their primary keys.

    This function should not be used if the model has neither a
    ForeignKey nor OneToOneField. ManyToManyField is not supported.

    Other Parameters
    ----------
    values : default=False
        Set as True if the QuerySet is passed after calling values() or
        values_list(). This will convert the QuerySet back to a list of
        model objects, instead of a list of dicts/lists. See ``Notes``
        for an important warning about performance.

    See Also
    --------
    qs_to_csv

    Raises
    ------
    ValueError
        If the values()/values_list() QuerySet is too large to convert.
    TypeError
        If values=False and the QuerySet called values()/values_list().

    Notes
    -----
    Passing ``values=True`` to this function will create a new query,
    checking for primary keys (PKs) that are in a list of all PKs from
    your original QuerySet. **This will add significant time if your
    QuerySet is large and will potentially not work**, depending on the
    size of your QuerySet and your database's capabilities.

    It is recommended to avoid this by not using values() or
    values_list() when calling this function. Note: if you make this
    change, ensure `values` is False.

    """
    response, fields = qs_to_csv_core(qs, filename, only, defer)

    if values:
        # See `Notes` in docstring for critical performance warning
        model = qs.model
        pk = model._meta.pk.name
        qs = list(qs.values())
        if qs:
            related_fields = [
                f.name for f in fields if f.many_to_one or f.one_to_one
            ]
            fields, headers = get_fields(fields, header, verbose)
            qs = (
                model.objects.select_related(*related_fields)
                .only(*fields)
                .filter(pk__in=(d[pk] for d in qs))
            )
    else:
        fields, headers = get_fields(fields, header, verbose)

    # Build csv file
    from csv import writer
    from django.db import reset_queries

    csv_writer = writer(response)
    if header:
        csv_writer.writerow(headers)

    try:
        for obj in qs:
            row = []

            for field in fields:
                data = getattr(obj, field)
                if callable(data):  # pragma: no cover
                    data = data()
                data = (
                    str(data, encoding="utf-8")
                    if isinstance(data, bytes)
                    else str(data)
                )
                row.append(data)
                reset_queries()

            csv_writer.writerow(row)
    except Exception as e:
        msg = str(e)
        if not values and "object has no attribute" in msg:
            raise TypeError(
                msg
                + " - The QuerySet was passed with values() or values_list()"
                " without specifying values=True."
            )
        elif values and "too many SQL variables" in msg:  # pragma: no cover
            raise ValueError(
                msg + " - The original QuerySet was too large to convert from"
                " values()/values_list() to a QuerySet of model objects."
                " This can be resolved by decreasing the size of your"
                " QuerySet or by not calling values/values_list() before"
                " calling this function then setting values=False."
            )
        raise e  # pragma: no cover

    return response
