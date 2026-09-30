"""Regression tests for the formerly missing inline polyglot content."""
import json,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P))
from embedded_seed import validate_embedded

class InlineSeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=(P/'SEED.md').read_text()
        cls.expected=json.loads((P/'EMBEDDED_CONTENT.json').read_text())
    def test_complete_actual_views(self):
        self.assertEqual(validate_embedded(self.text,self.expected)['ports'],['P'+str(i) for i in range(8)])
    def test_each_missing_view_rejected(self):
        for i in range(8):
            start='<!-- BEGIN_VIEW P'+str(i)+' -->\n';end='<!-- END_VIEW P'+str(i)+' -->'
            a,rest=self.text.split(start,1);_,b=rest.split(end,1)
            with self.subTest(port=i),self.assertRaises(AssertionError):validate_embedded(a+b,self.expected)
    def test_heading_only_view_rejected(self):
        start='<!-- BEGIN_VIEW P4 -->\n';end='<!-- END_VIEW P4 -->'
        a,rest=self.text.split(start,1);content,b=rest.split(end,1)
        broken=a+start+content.split('\n',1)[0]+'\n'+end+b
        with self.assertRaises(AssertionError):validate_embedded(broken,self.expected)
    def test_link_instead_of_actual_content_rejected(self):
        start='<!-- BEGIN_VIEW P5 -->\n';end='<!-- END_VIEW P5 -->'
        a,rest=self.text.split(start,1);content,b=rest.split(end,1)
        broken=a+start+content.split('\n',1)[0]+'\n[View elsewhere](../sigrun-v6/views/P5.md)\n'+end+b
        with self.assertRaises(AssertionError):validate_embedded(broken,self.expected)
    def test_duplicate_view_rejected(self):
        with self.assertRaises(AssertionError):validate_embedded(self.text+'\n# P0 OBSERVE — Old Norse\nreplacement',self.expected)
    def test_missing_core_seed_rejected(self):
        broken=self.text.replace('<!-- BEGIN_CORE_SEED -->','<!-- MISSING_CORE_SEED -->')
        with self.assertRaises(AssertionError):validate_embedded(broken,self.expected)
    def test_missing_stack_rejected(self):
        broken=self.text.replace('## Current technology and recovery map','## Missing component map')
        with self.assertRaises(AssertionError):validate_embedded(broken,self.expected)

if __name__=='__main__':unittest.main()
