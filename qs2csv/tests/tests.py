from csv import reader
from io import StringIO

from django.test import TestCase

from ..models import ForeignKeyModel, TestModel
from ..src.qs2csv import qs_to_csv, qs_to_csv_pd


class AllFunctionsTest(TestCase):
    def setUp(self):
        self.fkm = ForeignKeyModel.objects.create()
        self.afm = TestModel.objects.create(
            foreign_key=self.fkm,
            one_to_one_field=self.fkm,
        )
        self.afm.many_to_many_field.add(self.fkm)
        self.afm.save()
        self.qs = TestModel.objects.all()
        self.fields = TestModel._meta.local_fields

    def test_qs_to_csv(self):
        """Tests a standard export with default parameters.

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
        print(header_row)
        # self.assertEqual(header_row, ",".join(self.fields))

    def test_qs_to_csv_pd(self):
        """Tests a standard ``pandas`` export with default parameters.

        filename = "export.csv"
        only = []
        defer = []
        header = False
        verbose = True
        values = False
        """
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
