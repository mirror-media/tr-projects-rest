import os

# MONGO DATABASE SETTINGS FOR SAMPLE
MONGO_URI = 'mongodb://localhost:27017/keystone-test'
DATA_FORMAT = "a, %d %b %Y %H:%M:%S GMT+8"

OPTIMIZE_PAGINATION_FOR_SPEED = True

# The assets url is for production
ASSETS_URL = 'https://www.mirrormedia.com.tw/'
GCS_URL = 'https://storage.googleapis.com/mirrormedia-dev/'
ENV = 'dev'

REDIS_WRITE_HOST = '127.0.0.1'
REDIS_WRITE_PORT = 6379
REDIS_READ_HOST = '127.0.0.1'
REDIS_READ_PORT = 6379
REDIS_AUTH = 'foo'
REDIS_RULES = {
  "/posts": 604800,
  "/meta": 0,
  "/listing": 0,
  # cache for 7 days
  "/images": 604800,
  # "/albums": 604800,
  # "/partners": 604800,
  # "/externals": 604800,
  # "/event": 604800,
  # "/topics": 604800,
  # "/contacts": 604800,
  # cache for 10 mins
  "/albums": 600,
  "/event": 600,
  "/topics": 600,
  # cache for 24 hours
  "/partners": 86400,
  "/externals": 86400,
  "/contacts": 86400,
}

# ALLOW ACTIONS
DEBUG = False

ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE'] if DEBUG else ['GET']

slug_schema = {
  'slug': {
    'type': 'string',
  },
  'isCampaign': {
    'type': 'boolean',
  },
}

listing_schema = {
  'name': {
    'type': 'string',
  },
  'slug': {
    'type': 'string',
  },
  'title': {
    'type': 'string',
  },
  'subtitle': {
    'type': 'string',
  },
  'style': {
    'type': 'string',
  },
  'brief': {
    'type': 'dict',
    'schema': {
      "html": {
        "type": "string",
      },
    },
  },
  'sections': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'sections',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroImage': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroVideo': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'videos',
      'field': '_id',
      'embeddable': True
    },
  },
  'isFeatured': {
    'type': 'boolean',
  },
  'isAdvertised': {
    'type': 'boolean',
  },
  'isAdult': {
    'type': 'boolean',
  },
  'publishedDate': {
    'type': 'datetime',
  },
  'isCampaign': {
    'type': 'boolean',
  },
  'og_image': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'categories': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'postcategories',
            'field': '_id',
            'embeddable': True
         },
     },
  }
}

partner_schema = {
  'name': {
    'type': 'string',
  },
  'display': {
    'type': 'string',
  },
  'website': {
    'type': 'string',
  },
  'public': {
    'type': 'boolean',
  },
}

external_schema = {
  'name': {
    'type': 'string',
  },
  'title': {
    'type': 'string',
  },
  'subtitle': {
    'type': 'string',
  },
  'brief': {
    'type': 'string',
  },
  'content': {
    'type': 'string',
  },
  'partner': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'partners',
      'field': '_id',
      'embeddable': True
    },
  },
  'extend_byline': {
    'type': 'string',
  },
  'publishedDate': {
    'type': 'datetime',
  },
  'thumb': {
    'type': 'string',
  },
  'source': {
    'type': 'string',
  },
}

meta_schema = {
  'name': {
    'type': 'string',
  },
  'slug': {
    'type': 'string',
  },
  'title': {
    'type': 'string',
  },
  'subtitle': {
    'type': 'string',
  },
  'style': {
    'type': 'string',
  },
  'brief': {
    'type': 'dict',
    'schema': {
      "html": {
        "type": "string",
      },
    },
  },
  'tags': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'tags',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'sections': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'sections',
      'field': '_id',
      'embeddable': True
    },
  },
  'topics': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'topics',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'writers': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': 'name',
            'embeddable': True
        },
    },
  },
  'heroImage': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroVideo': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'videos',
      'field': '_id',
      'embeddable': True
    },
  },
  'categories': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'postcategories',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'relateds': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'meta',
            'field': '_id',
            'embeddable': True
         },
     }, 
  },
  'isFeatured': {
    'type': 'boolean',
  },
  'isAdult': {
    'type': 'boolean',
  },
  'isAdvertised': {
    'type': 'boolean',
  },
  'publishedDate': {
    'type': 'datetime',
  },
  'og_description': {
    'type': 'string',
  },
  'isCampaign': {
    'type': 'boolean',
  },
  'og_image': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  }
}

contact_schema = {
  'name': {
    'type': 'string',
  },
  'email': {
    'type': 'string',
    'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
  },
  'homepage': {
    'type': 'string',
  },
  'facebook': {
    'type': 'string',
  },
  'twitter': {
    'type': 'string',
  },
  'instantgram': {
    'type': 'string',
  },
  'bio': {
    'type': 'string',
  },
  'image': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
}

event_schema = {
  'name': {
    'type': 'string',
  },
  'state': {
    'type': 'string',
  },
  'eventType': {
    'type': 'string',
  },
  'startDate': {
    'type': 'datetime',
  },
  'endDate': {
    'type': 'datetime',
  },
  'embed': {
    'type': 'string',
  },
  'video': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'videos',
      'field': '_id',
      'embeddable': True
    },
  },
  'image': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'isFeatured': {
    'type': 'boolean',
  },
  'link': {
    'type': 'string',
  },
  'sections': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'sections',
            'field': '_id',
            'embeddable': True
        },
    },
  },
}

node_schema = {
  'name': {
    'type': 'string',
  },
  'subtitle': {
    'type': 'string',
  },
  'heroVideo': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'videos',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroImage': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroCaption': {
    'type': 'string',
  },
  'state': {
    'type': 'string',
  },
  'nodeDate': {
    'type': 'datetime',
  },
  'createTime': {
    'type': 'datetime',
  },
  'updatedAt': {
    'type': 'datetime',
  },
  'activity': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'activities',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'brief': {
    'type': 'dict',
    'schema': {
      "html": {
        "type": "string",
      },
    },
  },
  'content': {
    'type': 'dict',
    'schema': {
       "html": {
          "type": "string",
       },
     },  
  },
  'og_title': {
    'type': 'string',
  },
  'isFeatured': {
    'type': 'boolean',
  },
  'og_description': {
    'type': 'string',
  },
  'og_image': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
}

post_schema = {
  'name': {
    'type': 'string',
  },
  'slug': {
    'type': 'string',
  },
  'title': {
    'type': 'string',
  },
  'subtitle': {
    'type': 'string',
  },
  'heroVideo': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'videos',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroImage': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroCaption': {
    'type': 'string',
  },
  'state': {
    'type': 'string',
  },
  'albums': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'albums',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'sections': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'sections',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'writers': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'vocals': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'photographers': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'camera_man': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'designers': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'engineers': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'publishedDate': {
    'type': 'datetime',
  },
  'createTime': {
    'type': 'datetime',
  },
  'updatedAt': {
    'type': 'datetime',
  },
  'categories': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'postcategories',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'topics': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'topics',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'topics_ref': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'meta',
            'field': 'topics',
            'embeddable': True
         },
     },
  },
  'tags': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'tags',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'style': {
    'type': 'string',
  },
  'brief': {
    'type': 'dict',
    'schema': {
      "html": {
        "type": "string",
      },
    },
  },
  'content': {
    'type': 'dict',
    'schema': {
       "html": {
          "type": "string",
       },
     },  
  },
  'relateds': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'meta',
            'field': '_id',
            'embeddable': True
         },
     }, 
  },
  'extend_byline': {
    'type': 'string',
  },
  'og_title': {
    'type': 'string',
  },
  'isFeatured': {
    'type': 'boolean',
  },
  'isAdvertised': {
    'type': 'boolean',
  },
  'hiddenAdvertised': {
    'type': 'boolean',
  },
  'isAdult': {
    'type': 'boolean',
  },
  'lockJS': {
    'type': 'boolean',
  },
  'og_description': {
    'type': 'string',
  },
  'audio': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'audios',
      'field': '_id',
      'embeddable': True
    },
  },
  'og_image': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'device': {
    'type': 'string',
  },
  'adTrace': {
    'type': 'string',
    },
  'isAudioSiteOnly': {                                                                                                                                  
    'type': 'boolean',
  },    
  'isCampaign': {
    'type': 'boolean',
  },
}

readr_schema = {
  'name': {
    'type': 'string',
  },
  'slug': {
    'type': 'string',
  },
  'title': {
    'type': 'string',
  },
  'subtitle': {
    'type': 'string',
  },
  'heroVideo': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'videos',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroImage': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroCaption': {
    'type': 'string',
  },
  'state': {
    'type': 'string',
  },
  'albums': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'albums',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'sections': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'sections',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'writers': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'photographers': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'camera_man': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'designers': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'engineers': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'publishedDate': {
    'type': 'datetime',
  },
  'createTime': {
    'type': 'datetime',
  },
  'updatedAt': {
    'type': 'datetime',
  },
  'categories': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'postcategories',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'topics': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'topics',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'topics_ref': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'meta',
            'field': 'topics',
            'embeddable': True
         },
     },
  },
  'tags': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'tags',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'style': {
    'type': 'string',
  },
  'brief': {
    'type': 'dict',
    'schema': {
      "html": {
        "type": "string",
      },
    },
  },
  'content': {
    'type': 'dict',
    'schema': {
       "html": {
          "type": "string",
       },
     },  
  },
  'relateds': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'readrs',
            'field': '_id',
            'embeddable': True
         },
     }, 
  },
  'extend_byline': {
    'type': 'string',
  },
  'og_title': {
    'type': 'string',
  },
  'isFeatured': {
    'type': 'boolean',
  },
  'isAdvertised': {
    'type': 'boolean',
  },
  'hiddenAdvertised': {
    'type': 'boolean',
  },
  'isAdult': {
    'type': 'boolean',
  },
  'lockJS': {
    'type': 'boolean',
  },
  'og_description': {
    'type': 'string',
  },
  'og_image': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'device': {
    'type': 'string',
  },
  'adTrace': {
    'type': 'string',
  },
  'isCampaign': {
    'type': 'boolean',
  },
}

album_schema = {
  'name': {
    'type': 'string',
  },
  'title': {
    'type': 'string',
  },
  'leading': {
    'type': 'string',
  },
  'heroVideo': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'videos',
      'field': '_id',
      'embeddable': True
    },
  },
  'vocals': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'writers': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'photographers': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'contacts',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'extend_byline': {
    'type': 'string',
  },
  'heroImage': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'state': {
    'type': 'string',
  },
  'sections': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'sections',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'publishedDate': {
    'type': 'datetime',
  },
  'createTime': {
    'type': 'datetime',
  },
  'updatedAt': {
    'type': 'datetime',
  },
  'categories': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'postcategories',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'tags': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'tags',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'style': {
    'type': 'string',
  },
  'brief': {
    'type': 'dict',
    'schema': {
      "html": {
        "type": "string",
      },
    },
  },
  'og_title': {
    'type': 'string',
  },
  'isFeatured': {
    'type': 'boolean',
  },
  'sortOrder': {
    'type': 'integer',
  },
  'og_description': {
    'type': 'string',
  },
  'og_image': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
}

sections_schema = {
    'title': {
      'type': 'string',
    },
    'name': {
      'type': 'string',
    },
    'type': {
      'type': 'string',
      'allowed': ['articles', 'file', 'link']
    },
    'description': {
      'type': 'string',
    },
    'isFeatured': {
      'type': 'boolean',
    },
    'isAudioSiteOnly': {                                                                                                                                  
      'type': 'boolean',
    },    
    'image': {
      'type': 'objectid',
      'data_relation': {
        'resource': 'images',
        'field': '_id',
        'embeddable': True
      },
    },
    'heroImage': {
      'type': 'objectid',
      'data_relation': {
        'resource': 'images',
        'field': '_id',
        'embeddable': True
      },
    },
    'categories': {
      'type': 'list',
      'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'postcategories',
            'field': '_id',
            'embeddable': True
         },
       },
    },
    'extend_cats': {
      'type': 'list',
      'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'postcategories',
            'field': '_id',
            'embeddable': True
         },
       },
    },
    'topics': {
      'type': 'list',
      'schema': {
          'type': 'objectid',
          'data_relation': {
              'resource': 'topics',
              'field': '_id',
              'embeddable': True
           },
       }, 
    },
    'style': {
      'type': 'string',
    },
    'og_title': {
      'type': 'string',
    },
    'og_description': {
      'type': 'string',
    },
    'og_image': {
      'type': 'objectid',
      'data_relation': {
        'resource': 'images',
        'field': '_id',
        'embeddable': True
      },
    },
    'css': {
      'type': 'string',
    },
    'javascript': {
      'type': 'string',
    },
    'twitter': {
      'type': 'string',
    },
    'sortOrder': {
      'type': 'integer',
    }
}

videos_schema = {
  'title': {
    'type': 'string',
  },
  'description': {
    'type': 'string',
  },
  'coverPhoto': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'sections': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'sections',
            'field': '_id',
            'embeddable': True
        },
    },
  },
  'feed': {
    'type': 'boolean',
  },
  'categories': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'postcategories',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'video': {
    'type': 'dict',
    'schema': {
        'filetype': {
          'type': 'string',
        },
        'filename': {
          'type': 'string',
        },
        'originalname': {
          'type': 'string',
        },
        'path': {
          'type': 'string',
        },
        'projectId': {
          'type': 'string',
        },
        'size': {
          'type': 'string',
        },
        'url': {
          'type': 'string',
        },
    },
  },  
  'createTime': {
    'type': 'datetime',
  },
  'relateds': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'meta',
            'field': '_id',
            'embeddable': True
         },
     }, 
  },
  'updatedAt': {
    'type': 'datetime',
  },
  'publishedDate': {
    'type': 'datetime',
  },
  'state': {
    'type': 'string',
  },
  'tags': {
    'type': 'list',
    'schema': {
      'type': 'objectid',
      'data_relation': {
        'resource': 'tags',
        'field': '_id',
        'embeddable': True
      },
    },
  },
}

activities_schema = {
  'name': {
    'type': 'string',
  },
  'brief': {
    'type': 'dict',
    'schema': {
      "html": {
        "type": "string",
      },
    },
  },
  'heroVideo': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'videos',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroImage': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroCaption': {
    'type': 'string',
  },
  'topics': {
    'type': 'list',
    'schema': {
      'type': 'objectid',
      'data_relation': {
        'resource': 'topics',
        'field': '_id',
        'embeddable': True
      },
    }, 
  },
  'og_title': {
    'type': 'string',
  },
  'og_description': {
    'type': 'string',
  },
  'og_image': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
}

audiopromotions_schema = {
  'heroImage': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'href': {
    'type': 'string',
  }
}

voiceconfigs_schema = {
  'key': {
    'type': 'string',
  },
  'group': {
    'type': 'string',
  },
  'value': {
    'type': 'string',
  }
}

postcategories_schema = {
  'name': {
    'type': 'string',
  },
  'title': {
    'type': 'string',
  },
  'isFeatured': {
    'type': 'boolean',
  },
  'brief': {
    'type': 'dict',
    'schema': {
      "html": {
        "type": "string",
      },
    },
  },
  'heroVideo': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'videos',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroImage': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroCaption': {
    'type': 'string',
  },
  'og_title': {
    'type': 'string',
  },
  'og_description': {
    'type': 'string',
  },
  'og_image': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'isCampaign': {
    'type': 'boolean',
  },
  'style': {
    'type': 'string',
  },
  'css': {
    'type': 'string',
  },
  'javascript': {
    'type': 'string',
  }
}

audios_schema = {
  'title': {
    'type': 'string',
  },
  'description': {
    'type': 'string',
  },
  'audio': {
    'type': 'dict',
    'schema': {
        'filetype': {
          'type': 'string',
        },
        'filename': {
          'type': 'string',
        },
        'originalname': {
          'type': 'string',
        },
        'path': {
          'type': 'string',
        },
        'projectId': {
          'type': 'string',
        },
        'size': {
          'type': 'string',
        },
        'url': {
          'type': 'string',
        },
    },
  },  
  'coverPhoto': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'tags': {
    'type': 'list',
    'schema': {
      'type': 'objectid',
      'data_relation': {
        'resource': 'tags',
        'field': '_id',
        'embeddable': True
      },
    },
  },
}

tags_schema = {
  'name': {
    'type': 'string',
  },
  'leading': {
    'type': 'string',
  },
  'heroVideo': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'videos',
      'field': '_id',
      'embeddable': True
    },
  },
  'heroImage': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'isFeatured': {
    'type': 'boolean',
  },
  'og_title': {
    'type': 'string',
  },
  'og_description': {
    'type': 'string',
  },
  'og_image': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'style': {
    'type': 'string',
  },
  'css': {
    'type': 'string',
  },
  'javascript': {
    'type': 'string',
  },
  'sortOrder': {
    'type': 'integer',
  },
  'sections': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'sections',
            'field': '_id',
            'embeddable': True
        },
    },
  },  
}

topics_schema = {
  'name': {
    'type': 'string',
  },
  'subtitle': {
    'type': 'string',
  },
  'leading': {
    'type': 'string',
  },
  'type': {
    'type': 'string',
  },
  'brief': {
    'type': 'string',
  },
  'source': {
    'type': 'string',
  },
  'state': {
    'type': 'string',
  },
  'sort': {
    'type': 'string',
  },
  'heroVideo': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'videos',
      'field': '_id',
      'embeddable': True
    },
  },
  'sections': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'sections',
            'field': '_id',
            'embeddable': True
        },
    },
  },  
  'heroImage': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'isFeatured': {
    'type': 'boolean',
  },
  'og_title': {
    'type': 'string',
  },
  'og_description': {
    'type': 'string',
  },
  'og_image': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },
  'style': {
    'type': 'string',
  },
  'javascript': {
    'type': 'string',
  },
  'tags': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'tags',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'dfp': {
    'type': 'string',
  },
  'mobile_dfp': {
    'type': 'string',
  },
  'sortOrder': {
    'type': 'integer',
  }
}

audiomasters_schema = {
  'masters': {
    'type': 'objectid',
    'data_relation': {
        'resource': 'contacts',
        'field': '_id',
        'embeddable': True
     },
  },
  'sortOrder': {
    'type': 'integer',
  },
}

audiochoices_schema = {
  'choices': {
    'type': 'objectid',
    'data_relation': {
        'resource': 'posts',
        'field': '_id',
        'embeddable': True
     },
  },
  'sortOrder': {
    'type': 'integer',
  },
}

editorchoices_schema = {
  'choices': {
    'type': 'objectid',
    'data_relation': {
        'resource': 'listing',
        'field': '_id',
        'embeddable': True
     },
  },
  'sortOrder': {
    'type': 'integer',
  },
}

watchbrand_schema = {
  'name': {
    'type': 'string',
  },
}

watchfunction_schema = {
  'name': {
    'type': 'string',
  },
}
watch_schema = {
  'brand': {
    'type': 'objectid',
    'data_relation': {
        'resource': 'watchbrands',
        'field': '_id',
        'embeddable': True
     },
  },
  'watchfunction': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'watchfunctions',
            'field': '_id',
            'embeddable': True
         },
     }, 
  },
  'name': {
    'type': 'string',
  },
  'type': {
    'type': 'boolean',
  },
  'sex': {
    'type': 'string',
  },
  'price': {
    'type': 'string',
  },
  'movement': {
    'type': 'string',
  },
  'power': {
    'type': 'string',
  },
  'material': {
    'type': 'string',
  },
  'waterproof': {
    'type': 'string',
  },
  'watchImage': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'images',
      'field': '_id',
      'embeddable': True
    },
  },  
  'relateds': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'meta',
            'field': '_id',
            'embeddable': True
         },
     }, 
  },
  'content': {
    'type': 'string',
  },
}

choices_schema = {
  'pickDate': {
    'type': 'string',
  },
  'isPublished': {
    'type': 'boolean',
  },
  'choices': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'meta',
            'field': '_id',
            'embeddable': True
         },
     }, 
  },
}

image_schema = {
  'photographer': {
    'type': 'objectid',
    'data_relation': {
      'resource': 'contacts',
      'field': '_id',
      'embeddable': True
    },
  },
  'description': {
    'type': 'string',
  },
  'sale': {
    'type': 'Boolean',
  },
  'topics': {
    'type': 'list',
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'topics',
            'field': '_id',
            'embeddable': True
         },
     },
  },
  'tags': {
    'type': 'list',
    'schema': {
      'type': 'objectid',
      'data_relation': {
        'resource': 'tags',
        'field': '_id',
        'embeddable': True
      },
    },
  },
  'image': {
    'type': 'dict',
    'schema': {
      'artist': {
        'type': 'string',
      },
      'description': {
        'type': 'string',
      },
      'filename': {
        'type': 'string',
      },
      'filetype': {
        'type': 'string',
      },
      'height': {
        'type': 'number',
      },
      'width': {
        'type': 'number',
      },
      'size': {
        'type': 'number',
      },
      'url': {
        'type': 'string',
      }
    },
  },
  'createTime': {
    'type': 'datetime',
  },
  'keywords': {
    'type': 'string',
  },
}

posts = {
    'item_title': 'post',
    'additional_lookup': {
        'url': 'regex("[\w-]+")',
        'default_sort': [('publishedDate', -1)],
        'field': 'slug'
    },
    'datasource': {
        'source': 'posts',
        'filter': { '$or': [ { 'state': 'published' }, { 'state': 'invisible' } ] },
    },
    'resource_methods': ['GET'],
    'embedded_fields': ['vocals','writers','photographers','camera_man','audio', 'designers','engineers','heroImage', 'heroVideo', 'topics', 'sections', 'categories', 'tags', 'og_image', 'relateds'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': post_schema
}

readrs = {
    'item_title': 'readr',
    'additional_lookup': {
        'url': 'regex("[\w-]+")',
        'default_sort': [('publishedDate', -1)],
        'field': 'slug'
    },
    'datasource': {
        'source': 'readrs',
        'filter': { '$or': [ { 'state': 'published' }, { 'state': 'invisible' } ] },
    },
    'resource_methods': ['GET'],
    'embedded_fields': ['writers','photographers','camera_man','designers','engineers','heroImage', 'heroVideo', 'topics', 'sections', 'categories', 'tags', 'og_image', 'relateds'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': readr_schema
}

albums = {
    'item_title': 'album',
    'additional_lookup': {
        'url': 'regex("[\w-]+")',
        'default_sort': [('sortOrder', 1)],
        'field': 'name'
    },
    'datasource': {
        'source': 'albums',
        'filter': { '$or': [ { 'state': 'published' }, { 'state': 'invisible' } ] },
    },
    'resource_methods': ['GET'],
    'embedded_fields': ['heroImage', 'heroVideo', 'sections', 'writers', 'vocals', 'photographers', 'categories', 'tags', 'og_image'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': album_schema
}

nodes = {
    'item_title': 'node',
    'datasource': {
        'source': 'nodes',
        'filter': {'state': 'published'},
    },
    'resource_methods': ['GET'],
    'embedded_fields': ['heroImage', 'heroVideo', 'activity', 'og_image'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': node_schema
}

externals = {
    'item_title': 'external',
    'datasource': {
        'source': 'externals',
        'filter': {'state': 'published'},
    },
    'resource_methods': ['GET'],
    'embedded_fields': ['partner'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': external_schema
}

partners = {
    'item_title': 'partners',
    'datasource': {
        'source': 'partners',
    },
    'resource_methods': ['GET'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': partner_schema
}

slug = {
    'item_title': 'slug',
    'datasource': {
        'source': 'posts',
        'filter': { '$and': [ { 'state': 'published' }, { 'style': { '$nin': ['campaign'] } } ] },
    },
    'resource_methods': ['GET'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': slug_schema
}

event = {
    'item_title': 'event',
    'datasource': {
        'source': 'events',
        'filter': {'state': 'published'},
        'default_sort': [('startDate', -1)],
    },
    'resource_methods': ['GET'],
    'embedded_fields': ['image','sections', 'video'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': event_schema
}

listing = {
    'item_title': 'listing',
    'additional_lookup': {
        'url': 'regex("[\w-]+")',
        'default_sort': [('publishedDate', -1)],
        'field': 'slug'
    },
    'datasource': {
        'source': 'posts',
        'filter': { '$and': [ { 'state': 'published' }, { 'style': { '$nin': ['campaign' ] } } ] },
    },
    'resource_methods': ['GET'],
    'embedded_fields': ['heroImage', 'sections', 'writers', 'og_image', 'heroVideo','categories', 'tags'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': listing_schema
}

meta = {
    'item_title': 'meta',
    'additional_lookup': {
        'url': 'regex("[\w-]+")',
        'default_sort': [('publishedDate', -1)],
        'field': 'slug'
    },
    'datasource': {
        'source': 'posts',
        'filter': { '$and': [ { 'state': 'published' }, { 'style': { '$nin': ['campaign'] } } ] },
    },
    'resource_methods': ['GET'],
    'embedded_fields': ['heroImage','writers', 'topics','sections', 'categories','og_image', 'heroVideo', 'relateds', 'tags'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': meta_schema
}

drafts = {
    'item_title': 'draft',
    'additional_lookup': {
        'url': 'regex("[\w-]+")',
        'default_sort': [('publishedDate', -1)],
        'field': 'slug'
    },
    'datasource': {
        'source': 'posts',
        # 'filter': {'state': 'draft'},
    },
    'resource_methods': ['GET'],
    'embedded_fields': ['writers','photographers','designers','engineers','heroImage', 'heroVideo', 'topics', 'sections', 'categories', 'tags', 'og_image'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': post_schema
}

watchbrands = {
    'item_title': 'watchbrand',
    'datasource': {
        'source': 'watchbrands',
    },
    'resource_methods': ['GET'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': watchbrand_schema
}
watchfunctions = {
    'item_title': 'watchfunction',
    'datasource': {
        'source': 'watchfunctions',
    },
    'resource_methods': ['GET'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': watchfunction_schema
}
watches = {
    'item_title': 'watch',
    'datasource': {
        'source': 'watches',
        'default_sort': [('sortOrder', 1)],
        # 'filter': {'state': 'draft'},
    },
    'resource_methods': ['GET'],
    'embedded_fields': ['brand','watchfunction','watchImage', 'relateds'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': watch_schema
}

audiomasters = {
    'item_title': 'audiomaster',
    'datasource': {
        'source': 'audiomasters',
        'default_sort': [('sortOrder', 1)],
    },
    'embedded_fields': ['masters'],
    'resource_methods': ['GET'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': audiomasters_schema
}

audiochoices = {
    'item_title': 'audiochoice',
    'datasource': {
        'source': 'audiochoices',
        'default_sort': [('sortOrder', 1)],
    },
    'embedded_fields': ['choices'],
    'resource_methods': ['GET'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': audiochoices_schema
}

editorchoices = {
    'item_title': 'editorchoice',
    'datasource': {
        'source': 'editorchoices',
        'default_sort': [('sortOrder', 1)],
    },
    'embedded_fields': ['choices'],
    'resource_methods': ['GET'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': editorchoices_schema
}

choices = {
    'item_title': 'choice',
    'datasource': {
        'source': 'choices',
        'filter': {'isPublished': True},
    },
    'embedded_fields': ['choices'],
    'resource_methods': ['GET'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': choices_schema
}

topics = {
    'item_title': 'topic',
    'additional_lookup': {
        'url': 'regex(".+")',
        'field': 'name'
    },
    'datasource': {
        'source': 'topics',
        'filter': {'state': 'published'},
        'default_sort': [('sortOrder', 1)],
    },
    'resource_methods': ['GET'],
    'embedded_fields': ['heroImage', 'heroVideo', 'og_image'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': topics_schema
}

tags = {
    'item_title': 'tag',
    'additional_lookup': {
        'url': 'regex(".+")',
        'field': 'name'
    },
    'resource_methods': ['GET'],
    'embedded_fields': ['heroImage', 'heroVideo', 'og_image', 'sections'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': tags_schema
}

contacts = {
  'item_title': 'contact',
  'additional_lookup': {
    'url': 'regex(".+")',
    'field': 'name'
  },
  'resource_methods': ['GET'],
  'cache_control': 'max-age=1500,must-revalidate',
  'cache_expires': 1500,
  'allow_unknown': False,
  'embedded_fields': ['image'],
  'schema': contact_schema
}

voiceconfigs = {
  'item_title': 'voiceconfigs',
  'resource_methods': ['GET'],
  'cache_control': 'max-age=1500,must-revalidate',
  'cache_expires': 1500,
  'allow_unknown': False,
  'schema': voiceconfigs_schema
}

audiopromotions = {
    'item_title': 'audiopromotions',
    'resource_methods': ['GET'],
    'heroImage': {
        'type': 'objectid',
        'data_relation': {
          'resource': 'images',
          'field': '_id',
          'embeddable': True
        },
    },
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'embedded_fields': ['heroImage'],
    'schema': audiopromotions_schema,
}

postcategories = {
    'item_title': 'postcategory',
    'additional_lookup': {
        'url': 'regex(".+")',
        'field': 'name'
    },
    'resource_methods': ['GET'],
    'heroImage': {
        'type': 'objectid',
        'data_relation': {
          'resource': 'images',
          'field': '_id',
          'embeddable': True
        },
    },
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'embedded_fields': ['heroImage'],
    'schema': postcategories_schema,
}

activities = {
    'item_title': 'activity',
    'resource_methods': ['GET'],
    'embedded_fields': ['heroImage', 'heroVideo', 'topics'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': activities_schema,
}

sections = {
    'item_title': 'section',
    'additional_lookup': {
        'url': 'regex(".+")',
        'field': 'name'
    },
    'resource_methods': ['GET'],
    'embedded_fields': ['categories', 'heroImage', 'image', 'extend_cats', 'topics'],
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'allow_unknown': False,
    'schema': sections_schema,
}

images = {
    'resource_methods': ['GET'],
    'datasource': {'default_sort': [('createTime', -1)]},
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'schema': image_schema,
}

audios = {
    'resource_methods': ['GET'],
    'cache_control': 'max-age=1500,must-revalidate',
    'embedded_fields': ['coverPhoto'],
    'cache_expires': 1500,
    'schema': audios_schema,
}

videos = {
    'resource_methods': ['GET'],
    'datasource': {
        'source': 'videos',
        'filter': {'state': 'published'},
    },
    'cache_control': 'max-age=1500,must-revalidate',
    'cache_expires': 1500,
    'embedded_fields': ['categories', 'sections', 'tags', 'relateds', 'heroImage'],
    'schema': videos_schema,
}

DOMAIN = {
    'posts': posts,
    'readrs': readrs,
    'albums': albums,
    'drafts': drafts,
    'meta': meta,
    'listing': listing,
    'slug': slug,
    'tags': tags,
    'choices': choices,
    'editorchoices': editorchoices,
    'audiochoices': audiochoices,
    'audiomasters': audiomasters,
    'contacts': contacts,
    'topics': topics,
    'nodes': nodes,
    'postcategories': postcategories,
    'audiopromotions': audiopromotions,
    'voiceconfigs': voiceconfigs,
    'activities': activities,
    'images': images,
    'audios': audios,
    'videos': videos,
    'event': event,
    'sections': sections,
    'watches': watches,
    'watchbrands': watchbrands,
    'watchfunctions': watchfunctions,
    'partners': partners,
    'externals': externals,
    }

XML = False
IF_MATCH = False
X_DOMAINS = '*'
X_HEADERS = ['Content-Type']
PAGINATION_DEFAULT = 10

# override default settings for different env
if os.environ.get("CLUSTER_ENV") == "dev":
  from configs.dev import *
elif os.environ.get("CLUSTER_ENV") == "prod":
  from configs.prod import *
elif os.environ.get("CLUSTER_ENV") == "local":
  from configs.local import *
