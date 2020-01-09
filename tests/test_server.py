import unittest

from server import clean_item

class TestCleanItem(unittest.TestCase):
    '''test function clean_time'''
    def setUp(self):
        self.item = {
            '_updated': {},
            '_created': {},
            'relateds': [
                {
                    'title': 'foo',
                    'heroImage': 'foo',
                    'slug': 'bar',
                    '_id': 'bar',
                    'foo': 'bar'
                }
            ],
            'sections': [
                {
                    'extend_cats': 'foo',
                    'style': {},
                    'og_title': 'foo',
                    'og_description': 'foo',
                    'javascript': 'bar',
                    'css': 'bar',
                    'categories': {}
                }
            ]
        }
        self.expect = {
            'relateds': [
                {
                    'title': 'foo',
                    'heroImage': 'foo',
                    'slug': 'bar',
                    '_id': 'bar'
                }
            ],
            'sections': [{}]
        }

    def test_all(self):
        item = clean_item(self.item)
        self.assertEqual(item, self.expect)

if __name__ == '__main__':
    unittest.main()