import unittest
import json
from server import app
from pymongo import MongoClient
import os

class TestGetPosts(unittest.TestCase):
    '''test duplicate endpoint /getposts'''
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        # self.db = MongoClient(app.config['MONGO_URI'])['integration-test']
        
        # with open(os.path.abspath(os.path.dirname(__file__)) + '/fixtures/posts.json','r') as f:
        #     posts = json.load(f)
        #     self.db.posts.insert_many(posts)
    
    def tearDown(self):
        pass
        # self.db.posts.drop()

    def test_endpoint_exists(self):
        res = self.app.get('/getposts')
        self.assertEqual(res.status_code, 200)

        res_json = json.loads(res.get_data())
        if '_status' in res_json:
            self.assertNotEqual(res_json['_status'], 'ERR')
        if 'error' in res_json:
            self.assertNotEqual(res_json['_error']['code'], 404)

    def test_getposts_equal_posts(self):
        res_posts = self.app.get('/posts')
        res_getposts = self.app.get('/getposts')

        post_json = json.loads(res_posts.get_data())['_items']
        getpost_json = json.loads(res_getposts.get_data())['_items']
        for res, exp in zip(post_json, getpost_json):
            # href in _links is different
            del res['_links']
            del exp['_links']
            self.assertEqual(res, exp)


class TestGetMeta(unittest.TestCase):
    '''test duplicate endpoint /getmeta'''
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_endpoint_exists(self):
        res = self.app.get('/getmeta')
        self.assertEqual(res.status_code, 200)

        res_json = json.loads(res.get_data())
        if '_status' in res_json:
            self.assertNotEqual(res_json['_status'], 'ERR')
        if 'error' in res_json:
            self.assertNotEqual(res_json['_error']['code'], 404)

    def test_getmeta_equal_meta(self):
        res_meta = self.app.get('/meta')
        res_getmeta = self.app.get('/getmeta')
        
        # Only compare _items
        meta_json = json.loads(res_meta.get_data())['_items']
        getmeta_json = json.loads(res_getmeta.get_data())['_items']
        for res, exp in zip(meta_json, getmeta_json):
            # href in _links is different
            del res['_links']
            del exp['_links']
            self.assertEqual(res, exp)

class TestGetList(unittest.TestCase):
    '''test duplicate endpoint /getlist'''
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_endpoint_exists(self):
        res = self.app.get('/getlist')
        self.assertEqual(res.status_code, 200)

        res_json = json.loads(res.get_data())
        if '_status' in res_json:
            self.assertNotEqual(res_json['_status'], 'ERR')
        if 'error' in res_json:
            self.assertNotEqual(res_json['_error']['code'], 404)

    def test_getlist_equal_list(self):
        res_list = self.app.get('/listing')
        res_getlist = self.app.get('/getlist')

        list_json = json.loads(res_list.get_data())['_items']
        getlist_json = json.loads(res_getlist.get_data())['_items']
        for res, exp in zip(list_json, getlist_json):
            # href in _links is different
            del res['_links']
            del exp['_links']
            self.assertEqual(res, exp)
            

if __name__ == '__main__':
    unittest.main()