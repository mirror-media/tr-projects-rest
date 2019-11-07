## tr-projects-rest

twreporter middle-ware rest-api server

## Requirements 
``` shell
# linux
apt-get install libevent-dev
apt-get install python-all-dev
apt-get install python-pip
pip install -r requirements.txt

# mac
# install homebrew first
brew install python
/usr/local/bin/pip install -r requirements.txt
``` 

## Development

Python Eve configures itself through `settings.py` by default. Here is  some default settings for local MongoDB and Redis help you run the server locally. To start it, simply use:
``` shell
# set mongo database in settings.py
python server.py

# mac
/usr/local/bin/python server.py
```

If there are ip-address/password different from defaults, set them in `configs/local.py` to overwrite `settings.py`, and start the server setting environment variable `CLUSTER_ENV`:
```shell
CLUSTER_ENV=local python server.py
```

In `dev` and `prod` cluster, `CLUSTER_ENV` will be set to `dev` and `prod` correspondinly, and server will load `dev.py` or `prod.py` based on `CLUSTER_ENV`.

## Deploy
### Production

``` shell
CLUSTER_ENV=prod uwsgi --ini uwsgi.ini &
```
### Test uwsgi settings with virtualenv locally

```shell
uwsgi --ini uwsgi.ini -H [PATH_TO_VIRTUALENV]
```
`CLUSTER_ENV` could be used here, too.

## Script

- scripts have been moved to https://github.com/twreporter/tr-projects-crontab

## Examples

- http://localhost:8080/posts
- http://localhost:8080/posts/the-post-slug
- http://localhost:8080/posts?embedded={"authors":1,"tags":1,"categories":1}
- http://localhost:8080/posts?content_type=html
- http://localhost:8080/contacts?where={"_id":{"$in":["56cec38678c3ee45f715b077","56cec37a78c3ee45f715afd6"]}}
- http://localhost:8080/contacts?where={"_id":{"$in":["56cec38678c3ee45f715b077","56cec37a78c3ee45f715afd6"]}, "email":"feugiat.nec.diam@idante.org"}
- http://localhost:8080/posts?where={"tags":{"$in":["56d01094b4710c3602715ad2"]}}
- http://localhost:8080/users/
- http://localhost:8080/contacts

### Show nested entities in response.
- http://localhost:8080/posts?embedded={"authors":1,"tags":1,"categories":1}
- http://localhost:8080/posts/the-post-slug?embedded={"authors":1,"tags":1,"categories":1}
 

### Conditional selection
- http://localhost:8080/contacts?where={"_id":{"$in":["56cec38678c3ee45f715b077","56cec37a78c3ee45f715afd6"]}}
- http://localhost:8080/contacts?where={"_id":{"$in":["56cec38678c3ee45f715b077","56cec37a78c3ee45f715afd6"]},"email":"feugiat.nec.diam@idante.org"}
- http://localhost:8080/posts?where={%22tags%22:{%22$in%22:[%2256d01094b4710c3602715ad2%22]}}


# License

MIT http://mit-license.org 
