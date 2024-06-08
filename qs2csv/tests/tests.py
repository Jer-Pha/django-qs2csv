from csv import reader
from io import StringIO

from django.test import TestCase

from ..models import ForeignKeyModel, TestModel
from ..src.qs2csv import qs_to_csv, qs_to_csv_pd, qs_to_csv_rel_str


class AllFunctionsTest(TestCase):
    """Tests all package functions."""

    def setUp(self):
        """Sets up test data."""
        self.fkm = ForeignKeyModel.objects.create()
        self.afm = TestModel.objects.create(
            foreign_key=self.fkm,
            one_to_one_field=self.fkm,
        )
        self.afm.many_to_many_field.add(self.fkm)
        self.afm.save()
        self.qs = TestModel.objects.all()
        self.fields = TestModel._meta.local_fields

    def test_model_str(self):
        """Tests model __str__ accuracy."""
        self.assertEqual(str(self.fkm), f"FK Model #{self.fkm.pk}")
        self.assertEqual(str(self.afm), f"AF Model #{self.afm.pk}")

    def test_qs_to_csv(self):
        """Tests qs_to_csv() with default parameters.

        filename = "export.csv"
        only = []
        defer = []
        header = False
        verbose = True
        values = False
        """
        response = qs_to_csv(self.qs)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Content-Type", response.headers)
        self.assertIn("export.csv", response.headers["Content-Disposition"])
        content = response.content.decode("utf-8")
        cvs_reader = reader(StringIO(content))
        body_rows = list(cvs_reader)
        header_row = body_rows.pop(0)
        self.assertFalse(body_rows)
        self.assertIn("1 day, 0:00:00", header_row)

    def test_qs_to_csv_pd(self):
        """Tests qs_to_csv_pd() with default parameters."""
        response = qs_to_csv_pd(self.qs)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Content-Type", response.headers)
        self.assertIn("export.csv", response.headers["Content-Disposition"])
        content = response.content.decode("utf-8")
        cvs_reader = reader(StringIO(content))
        body_rows = list(cvs_reader)
        header_row = body_rows.pop(0)
        self.assertFalse(body_rows)
        self.assertIn("1 days", header_row)

        # self.assertEqual(header_row, ",".join(self.fields))

    def test_qs_to_values(self):
        """Tests qs_to_values() when ``values = True``."""
        with self.assertRaises(TypeError):
            qs_to_csv(self.qs, values=True)
        with self.assertRaises(TypeError):
            qs_to_csv_pd(self.qs.values_list(), values=True)

    def test_filename_format(self):
        """Tests filename formatting errors."""
        f1 = ("a") * 252
        with self.assertRaises(ValueError):
            qs_to_csv(self.qs, filename=f1)
        with self.assertRaises(ValueError):
            qs_to_csv_pd(self.qs, filename=f1)
        f2 = "1<2.csv"
        with self.assertRaises(ValueError):
            qs_to_csv(self.qs, filename=f2)
        with self.assertRaises(ValueError):
            qs_to_csv_pd(self.qs, filename=f2)
        f3 = "file."
        with self.assertRaises(ValueError):
            qs_to_csv(self.qs, filename=f3)
        with self.assertRaises(ValueError):
            qs_to_csv_pd(self.qs, filename=f3)

        response = qs_to_csv(self.qs, filename="x", header=True)
        self.assertIn(".csv", response.headers["Content-Disposition"])
        content = response.content.decode("utf-8")
        cvs_reader = reader(StringIO(content))
        body_rows = list(cvs_reader)
        header_row = body_rows.pop(0)
        self.assertIn("Big Auto", header_row)

    def test_only_param(self):
        """Tests qs_to_csv() with only and defer parameters."""
        only = [
            "char_field",
            "boolean_field",
            "foreign_key",
            "many_to_many_field",
            "text_field",
        ]
        defer = ["text_field"]
        response = qs_to_csv(
            self.qs.values(),
            only=only,
            defer=defer,
            header=True,
            verbose=False,
        )
        content = response.content.decode("utf-8")
        cvs_reader = reader(StringIO(content))
        body_rows = list(cvs_reader)
        header_row = body_rows.pop(0)
        self.assertEqual(len(header_row), 3)
        self.assertEqual(len(body_rows), 1)

    def test_only_param_pd(self):
        """Tests qs_to_csv_pd() with only param and verbose header."""
        only = [
            "char_field",
            "boolean_field",
            "foreign_key",
            "many_to_many_field",
            "text_field",
        ]
        response = qs_to_csv_pd(self.qs.values_list(), only=only, header=True)
        content = response.content.decode("utf-8")
        cvs_reader = reader(StringIO(content))
        body_rows = list(cvs_reader)
        header_row = body_rows.pop(0)
        self.assertIn("Text", header_row)
        self.assertEqual(len(body_rows[0]), 4)

    def test_defer_param(self):
        """Tests qs_to_csv() with defer parameter."""
        defer = ["decimal_field", "generic_ip_field"]
        response = qs_to_csv(self.qs.values_list(), defer=defer)
        content = response.content.decode("utf-8")
        cvs_reader = reader(StringIO(content))
        body_rows = list(cvs_reader)
        self.assertEqual(len(body_rows[-1]), 14)

    def test_defer_param_pd(self):
        """Tests qs_to_csv_pd() with defer parameter."""
        defer = ["duration_field", "many_to_many_field", "date_field"]
        response = qs_to_csv_pd(self.qs.values(), defer=defer)
        content = response.content.decode("utf-8")
        cvs_reader = reader(StringIO(content))
        body_rows = list(cvs_reader)
        self.assertEqual(len(body_rows[0]), 14)

    def test_qs_to_csv_rel_str(self):
        """Tests qs_to_csv_rel_str() with multiple params."""
        only = []
        defer = ["char_field"]
        response = qs_to_csv_rel_str(
            self.qs,
            header=True,
            filename="tests.py",
            only=only,
            defer=defer,
            verbose=False,
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        cvs_reader = reader(StringIO(content))
        body_rows = list(cvs_reader)
        header_row = body_rows.pop(0)
        self.assertIn("date_field", header_row)
        self.assertNotIn("many_to_many_field", header_row)
        self.assertIn("1 day, 0:00:00", body_rows[0])

    def test_qs_to_csv_rel_str_val(self):
        """Tests qs_to_csv_rel_str() with values = True."""
        response = qs_to_csv_rel_str(self.qs.values_list(), values=True)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        cvs_reader = reader(StringIO(content))
        body_rows = list(cvs_reader)
        self.assertEqual(len(body_rows), 1)
        self.assertEqual(len(body_rows[0]), 16)

        response = qs_to_csv_rel_str(
            self.qs,
            values=True,
            only=["char_field"],
            header=True,
            verbose=False,
        )
        self.assertEqual(response.status_code, 200)
        content2 = response.content.decode("utf-8")
        cvs_reader2 = reader(StringIO(content2))
        body_rows2 = list(cvs_reader2)
        header_row2 = body_rows2.pop(0)
        self.assertEqual(len(header_row2), 1)
        self.assertEqual(header_row2[-1], "char_field")
        self.assertEqual(len(body_rows2[-1]), 1)

    def test_qs_to_csv_rel_str_err(self):
        """Tests qs_to_csv_rel_str() for raised errors."""
        with self.assertRaises(TypeError):
            qs_to_csv_rel_str(self.qs.values())
        with self.assertRaises(TypeError):
            qs_to_csv_rel_str(self.qs.values_list())
