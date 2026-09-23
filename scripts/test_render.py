import copy
import json
import unittest
import tempfile
from pathlib import Path
from render import validate, render

class DataContractTest(unittest.TestCase):
    def setUp(self):
        self.doc=json.loads((Path(__file__).parent.parent/'examples/demo.json').read_text())
    def test_demo_valid(self):
        self.assertEqual(validate(self.doc),[])
    def test_missing_stays_missing(self):
        before=copy.deepcopy(self.doc)
        validate(self.doc)
        self.assertEqual(self.doc,before)
        self.assertIsNone(self.doc['pages'][1]['charts'][1]['values'][2])
    def test_overlap_cannot_be_stacked(self):
        self.doc['pages'][0]['charts'][2]['values']=[60,30,20]
        with self.assertRaisesRegex(ValueError,'sum to 100'):validate(self.doc)
    def test_exclusive_must_be_declared(self):
        del self.doc['pages'][0]['charts'][2]['exclusive']
        with self.assertRaisesRegex(ValueError,'exclusive'):validate(self.doc)
    def test_increasing_funnel_rejected(self):
        self.doc['pages'][0]['charts'][0]['values']=[100,200,50]
        with self.assertRaisesRegex(ValueError,'non-increasing'):validate(self.doc)
    def test_zero_funnel_start_rejected(self):
        self.doc['pages'][0]['charts'][0]['values']=[0,0,0]
        with self.assertRaisesRegex(ValueError,'positive'):validate(self.doc)
    def test_nonfinite_rejected(self):
        self.doc['pages'][0]['charts'][0]['values'][0]=float('nan')
        with self.assertRaisesRegex(ValueError,'finite'):validate(self.doc)
    def test_missing_base_rejected(self):
        del self.doc['pages'][0]['charts'][0]['base']
        with self.assertRaisesRegex(ValueError,'base'):validate(self.doc)
    def test_irregular_times_rejected(self):
        self.doc['pages'][1]['charts'][1]['equally_spaced']=False
        with self.assertRaisesRegex(ValueError,'equally spaced'):validate(self.doc)
    def test_unknown_population_visible_warning(self):
        self.doc['pages'][0]['charts'][0]['base']='База не указана'
        self.assertTrue(validate(self.doc))
    def test_decimals_rejects_boolean_and_float(self):
        for value in (True, False, 1.0):
            with self.subTest(value=value):
                self.doc['pages'][0]['charts'][0]['decimals']=value
                with self.assertRaisesRegex(ValueError,'decimals'):validate(self.doc)

class PublicationTest(unittest.TestCase):
    def setUp(self):
        self.doc={'pages':[{'title':'Regression report','period':'Week 1',
            'source':'Synthetic regression fixture','charts':[{
                'type':'bar','title':'Activation','base':'Synthetic eligible users',
                'unit':'%','labels':['Group A'],'values':[10]}]}]}
    def test_existing_report_is_preserved_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'report'
            render(self.doc,out)
            before={p.name:p.read_bytes() for p in out.iterdir()}
            self.doc['pages'][0]['charts'][0]['values']=[14]
            with self.assertRaisesRegex(ValueError,'new or empty'):
                render(self.doc,out)
            self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir()})
    def test_layout_failure_publishes_no_partial_files(self):
        self.doc['pages'][0]['charts'][0]['unit']='verylongunit'*20
        for preexisting_empty in (False, True):
            with self.subTest(preexisting_empty=preexisting_empty), tempfile.TemporaryDirectory() as tmp:
                out=Path(tmp)/'report'
                if preexisting_empty:out.mkdir()
                with self.assertRaisesRegex(ValueError,'outside canvas'):
                    render(self.doc,out)
                self.assertEqual(out.exists(),preexisting_empty)
                self.assertEqual(list(out.iterdir()) if out.exists() else [],[])
                self.assertEqual(list(Path(tmp).iterdir()),[out] if preexisting_empty else [])
    def test_multiline_period_labels_reserve_more_page_height(self):
        from PIL import Image
        chart=self.doc['pages'][0]['charts'][0]
        chart.update(type='line',labels=['W1','W2','W3'],values=[0,None,14],
                     equally_spaced=True,note='Missing observations are not interpolated.')
        with tempfile.TemporaryDirectory() as tmp:
            short=Path(tmp)/'short'
            long=Path(tmp)/'long'
            render(self.doc,short)
            chart['labels']=[f'{word} полная календарная неделя сентября'
                             for word in ('Первая','Вторая','Третья')]
            render(self.doc,long)
            with Image.open(short/'page-01.png') as a, Image.open(long/'page-01.png') as b:
                self.assertEqual(a.width,b.width)
                self.assertGreater(b.height-a.height,60,
                    'Multiline period labels need extra space before the missing-data note')
            saved=json.loads((long/'input.json').read_text())
            self.assertEqual(saved['pages'][0]['charts'][0]['values'],[0,None,14])

if __name__=='__main__':unittest.main()
