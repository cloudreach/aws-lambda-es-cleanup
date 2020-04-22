import datetime
import unittest

import es_cleanup

IDX_REGEX = '.*'
IDX_FORMAT1 = '%Y.%m.%d'
SKIP_IDX_REGEX = 'kibana*'

decider = es_cleanup.DeleteDecider(delete_after=4,
                                   idx_format=IDX_FORMAT1,
                                   idx_regex=IDX_REGEX,
                                   skip_idx_regex=SKIP_IDX_REGEX,
                                   today=datetime.date(2019, 12, 19))


class TestShouldDelete(unittest.TestCase):
    def test_should_be_deleted(self):
        tuple = decider.should_delete({"index": "k8s-2019.12.14"})
        self.assertTrue(tuple[0])

    def test_should_not_be_deleted(self):
        tuple = decider.should_delete({"index": "k8s-2019.12.15"})
        self.assertFalse(tuple[0])

    def test_should_raise_value_error(self):
        with self.assertRaises(ValueError):
            decider.should_delete({"index": "k8s-2019-12-15"})

    def test_should_skip_indes(self):
        tuple = decider.should_delete({"index": ".kibana"})
        self.assertFalse(tuple[0])
        self.assertTrue("matches skip condition" in tuple[1])


if __name__ == '__main__':
    unittest.main()
