# 10장 페브릭을 이용한 배포 자동화

- 배포 자동화는 스테이징 테스트에 있어 핵심이다.
- 배포 절차를 반복 실행함으로 운영 환경에서도 정상적으로 동작하는 사이트를 배포 가능하다.

- 페브릭(Fabric)?
  - 서버에서 명령어를 자동으로 실행할 수 있게 해주는 툴

Fabric은 서버에서 실행하려는 명령을 자동화 할 수있는 도구이다. `fabric3`는 fabric의 Python3 버전이다.

```sh
pip install fabric3
```

일반적 설정은 `fabfile.py` 에서 작성한다. 이 파일에 작성된 함수들이 `fab` 같은 커맨드라인 툴에서 실행된다.

```sh
fab function_name,host=SERVER_ADDRESS
```

function_name 이라는 함수를 호출해서 SERVER_ADDRESS 서버에 전달한다.

## 배포를 위한 페브릭 스크립트 파헤치기(예제 : [10-01](./10-01))

예제 파일을 보며 페브릭이 어떻게 동작하는 지 살펴보자.

### [deploy_tools/fabfile.py](./10-01/deploy_tools/fabfile.py)

```py
import random
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run

REPO_URL = 'https://github.com/PilhwanKim/superlists.git'  

def deploy():
    site_folder = f'/home/{env.user}/sites/{env.host}'  
    run(f'mkdir -p {site_folder}')  
    with cd(site_folder):  
        _get_latest_source()
        _update_virtualenv()
        _create_or_update_dotenv()
        _update_static_files()
        _update_database()
```

- `env.user`에는 서버에 로그인 할 때 사용하는 사용자 이름. `env.host`는 커맨드라인에서 지정한 서버의 주소(예 : superlists.ml).
- `run`은 가장 일반적인 Fabric 명령이다. "서버에서 이 쉘 명령을 실행하십시오" 라고 명시하는 것. 이 장의 실행 명령은 마지막 두 명령에서 수동으로 수행 한 많은 명령을 복제합니다.
- `mkdir -p`는 유용한 `mkdir`옵션으로 더 좋은 이유가 있다.
  - 디렉토리를 여러 수준으로 만들 수 있으며 필요한 경우에만 만들 수 있다.
  - `mkdir -p /tmp/foo/bar`는 필요한 경우 디렉토리 표시 줄과 상위 디렉토리 `foo`를 만든다. `bar`가 이미 존재하는 경우에도 에러 처리 하지 않는다.
- `cd`는 "이 작업 디렉토리 내에서 다음 모든 명령문을 실행하십시오"라는 패브릭 컨텍스트 관리자이다.

이후의 helper function 은 자기 설명적(self-descriptive) 이름을 가지고 있다.

fabfile의 모든 함수는 명령줄에서 호출 할 수 있기 때문에, 밑줄 표기법을 사용하여 해당 함수가 fabfile의 "공용 API"의 일부가 아님을 나타낸다.

순서대로 함수들의 내용을 각각 살펴 보자.

### Git으로 소스 코드 받기

```py
def _get_latest_source():
    if exists('.git'):  
        run('git fetch')  
    else:
        run(f'git clone {REPO_URL} .')  
    current_commit = local("git log -n 1 --format=%H", capture=True)  
    run(f'git reset --hard {current_commit}')
```

- `exist`는 디렉토리 또는 파일이 서버에 이미 존재하는지 확인한다. `.git` 숨겨진 폴더를 찾아서 repo가 ​​사이트 폴더에 이미 복제되었는지 확인한다.
- 기존 git repo 가 있다면 `git fetch`는 명령으로 모든 최신 커밋을 가져온다(git pull과 같지만 라이브 소스 트리를 즉시 업데이트하지는 않음).
- 기존 git repo 가 없다면, repo URL과 함께 `git clone`을 사용하여 새로운 소스 트리를 가져온다.
- Fabric의 `local` 명령은 로컬 PC에서 명령을 실행한다. `subprocess.call`을 래핑한 것으로 매우 편리하다. 여기서는 `git log` 출력을 캡처하여 로컬 Tree에 있는 현재 커밋의 ID를 얻는다. 이것은 로컬 장비에서 체크아웃한 상태와 동일한 상태로 서버가 종료됨을 의미한다(단 서버에 push 한 상태여아 한다)
- `reset --hard` 이용하여 서버의 코드 디렉터리에 발생한 모든 변경을 초기화한다

### Virtualenv 업데이트

```py
def _update_virtualenv():
    if not exists('virtualenv/bin/pip'):  
        run(f'python3.6 -m venv virtualenv')
    run('./virtualenv/bin/pip install -r requirements.txt')
```

- virtualenv 폴더 내부에서 `pip` 실행 파일이 있는지 확인하는 방법으로 pip 실행 파일을 찾는다.
- 그런 다음 이전과 같이 `pip install -r`을 사용한다.

### 필요한 경우에 새 .env 파일 만들기

```py
def _create_or_update_dotenv():
    append('.env', 'DJANGO_DEBUG_FALSE=y')  
    append('.env', f'SITENAME={env.host}')
    current_contents = run('cat .env')  
    if 'DJANGO_SECRET_KEY' not in current_contents:  
        new_secret = ''.join(random.SystemRandom().choices(  
            'abcdefghijklmnopqrstuvwxyz0123456789', k=50
        ))
        append('.env', f'DJANGO_SECRET_KEY={new_secret}')
```

- `append` 명령은 조건부로 파일에 줄을 추가한다(해당 줄이 없는 경우)
- `DJANGO_SECRET_KEY`의 경우 먼저 파일에 이미 항목이 있는지 수동으로 확인한다.
- key 가 없는 경우, 이전의 단일 라이너를 참고하여 새로운 단일 라이너로 key를 생성한다(새 키와 기존의 잠재적인 키가 동일하지 않기 때문에 `append` 명령이 유효하다).

### 정적 파일 업데이트

```py
def _update_static_files():
    run('./virtualenv/bin/python manage.py collectstatic --noinput')  
```

- `Django manage.py` 명령을 실행해야 할 때마다 virtualenv 버전의 Python을 사용하여 시스템 버전이 아닌 Django의 virtualenv 버전을 가져온다.

### 필요한 경우에 데이터베이스 마이그레이션

```py
def _update_database():
    run('./virtualenv/bin/python manage.py migrate --noinput')
```

- `--noinput`은 Fabric이 처리하기 어려운 대화형 yes/no 확인을 건너뛴다.

### 자동화 스크립트 실행해보기

먼저 fabfile.py를 git repo에 적용하자.

```sh
$ git push
```

이제 스테이징 사이트에서 스크립트를 실행해보자.

```sh
$ cd ~/sites/staging.superlists.ml/deploy_tools/

# fab deploy:host=webapp@superlists.ml 으로 실행하도록 나오는데 fab 명령어로 되질 않아서 다음과 같이 함
$ python3 -m fabric deploy:host=webapp@staging.superlists.ml
[webapp@staging.superlists.ml] Executing task 'deploy'
[webapp@staging.superlists.ml] run: mkdir -p
/home/webapp/sites/superlists-staging.ottg.eu
[webapp@staging.superlists.ml] run: git fetch
[webapp@staging.superlists.ml] out: remote: Counting objects: [...]
[webapp@staging.superlists.ml] out: remote: Compressing objects: [...]
[localhost] local: git log -n 1 --format=%H
[webapp@staging.superlists.ml] run: git reset --hard
[...]
[webapp@staging.superlists.ml] out: HEAD is now at [...]
[webapp@staging.superlists.ml] out:
[webapp@staging.superlists.ml] run: ./virtualenv/bin/pip install -r
requirements.txt
[webapp@staging.superlists.ml] out: Requirement already satisfied:
django==1.11.13 in ./virtualenv/lib/python3.6/site-packages (from -r
requirements.txt (line 1))
[webapp@staging.superlists.ml] out: Requirement already satisfied:
gunicorn==19.8.1 in ./virtualenv/lib/python3.6/site-packages (from -r
requirements.txt (line 2))
[webapp@staging.superlists.ml] out: Requirement already satisfied: pytz
in ./virtualenv/lib/python3.6/site-packages (from django==1.11.13->-r
requirements.txt (line 1))
[webapp@staging.superlists.ml] out:
[webapp@staging.superlists.ml] run: ./virtualenv/bin/python manage.py
collectstatic --noinput
[webapp@staging.superlists.ml] out:
[webapp@staging.superlists.ml] out: 0 static files copied to
'/home/webapp/sites/superlists-staging.ottg.eu/static', 15 unmodified.
[webapp@staging.superlists.ml] out:
[webapp@staging.superlists.ml] run: ./virtualenv/bin/python manage.py
migrate --noinput
[webapp@staging.superlists.ml] out: Operations to perform:
[webapp@staging.superlists.ml] out:   Apply all migrations: auth,
contenttypes, lists, sessions
[webapp@staging.superlists.ml] out: Running migrations:
[webapp@staging.superlists.ml] out:   No migrations to apply.
[webapp@staging.superlists.ml] out:
```

이 스크립트는 몇번 반복 실행해도 같은 결과를 만들어내는데 멱등성(idempotent) 이 있기 때문이다.

### 라이브 배포

동일한 명령어로 라이브 배포를 해보자.

```sh
$ fab deploy:host=webapp@superlists.ml
[webapp@superlists.ml] Executing task 'deploy'
[webapp@superlists.ml] run: mkdir -p
/home/webapp/sites/superlists.ml
[webapp@superlists.ml] run: git clone https://github.com/PilhwanKim/superlists.git .
[webapp@superlists.ml] out: Cloning into '.'...
[...]
[webapp@superlists.ml] out: Receiving objects: 100% [...]
[...]
[webapp@superlists.ml] out: Resolving deltas: 100% [...]
[webapp@superlists.ml] out:
[localhost] local: git log -n 1 --format=%H
[webapp@superlists.ml] run: git reset --hard [...]
[webapp@superlists.ml] out: HEAD is now at [...]
[webapp@superlists.ml] out:
[webapp@superlists.ml] run: python3.6 -m venv virtualenv
[webapp@superlists.ml] run: ./virtualenv/bin/pip install -r
requirements.txt
[webapp@superlists.ml] out: Collecting django==1.11.13 [...]
[webapp@superlists.ml] out:   Using cached [...]
[webapp@superlists.ml] out: Collecting gunicorn==19.8.1 [...]
[webapp@superlists.ml] out:   Using cached [...]
[webapp@superlists.ml] out: Collecting pytz [...]
[webapp@superlists.ml] out:   Using cached [...]
[webapp@superlists.ml] out: Installing collected packages: pytz, django,
gunicorn
[webapp@superlists.ml] out: Successfully installed django-1.11
gunicorn-19.7.1 pytz-2017.3

[webapp@superlists.ml] run: echo 'DJANGO_DEBUG_FALSE=y' >> "$(echo .env)"
[webapp@superlists.ml] run: echo 'SITENAME=superlists.ml' >> "$(echo .env)"
[webapp@superlists.ml] run: echo 'DJANGO_SECRET_KEY=[...]'
[webapp@superlists.ml] run: ./virtualenv/bin/python manage.py
collectstatic --noinput
[webapp@superlists.ml] out: Copying
'/home/webapp/sites/superlists.ml/lists/static/base.css'
[...]
[webapp@superlists.ml] out: 15 static files copied to
'/home/webapp/sites/superlists.ml/static'.
[webapp@superlists.ml] out:

[webapp@superlists.ml] run: ./virtualenv/bin/python manage.py migrate
[...]
[webapp@superlists.ml] out: Operations to perform:
[webapp@superlists.ml] out:   Apply all migrations: auth, contenttypes,
lists, sessions
[webapp@superlists.ml] out: Running migrations:
[webapp@superlists.ml] out:   Applying contenttypes.0001_initial... OK
[webapp@superlists.ml] out:   Applying
contenttypes.0002_remove_content_type_name... OK
[webapp@superlists.ml] out:   Applying auth.0001_initial... OK
[webapp@superlists.ml] out:   Applying
auth.0002_alter_permission_name_max_length... OK
[...]
[webapp@superlists.ml] out:   Applying lists.0004_item_list... OK
[webapp@superlists.ml] out:   Applying sessions.0001_initial... OK
[webapp@superlists.ml] out:


Done.
Disconnecting from webapp@superlists.ml... done.
```

다른 경로(~/sites/superlists.ml) 로 잘 배포가 되는 것을 볼 수 있다.

장에서 언급한 배포 절차를 반복 실행이 가능함을 확인한 것이다.

### 프로비저닝 : sed를 사용하여 Nginx 및 Gunicorn 설정

이제 남은 할일은 9장에서 만든 템플릿 파일들을 이용해서 Nginx 가상 호스트와 Systemd 서비스 config 파일들을 만들어서 실행시키는 일이다.

```sh
webapp@server:$ cat ./deploy_tools/nginx.template.conf \
    | sed "s/DOMAIN/superlists.ml/g" \
    | sudo tee /etc/nginx/sites-available/superlists.ml
```

`sed` ("stream editor") - 텍스트 스트림을 가져와서 편집함.

- `s/replaceme/withthis/g` 구문으로 사이트 주소 대신 DOMAIN 문자열을 대체하도록 요청한다.
- cat은 파일을 출력하고 이를 sed 프로세스로 파이프 (|)한다.
- tee를 사용하여 입력을 파일에 쓰는 루트 사용자 프로세스 (sudo)로 출력함. `sites-available` 디렉터리의 nginx config 파일을 최종 생성 한다.

symlink를 이용해서 Nginx 설정파일을 활성화 한다.

```sh
webapp@server:$ sudo ln -s /etc/nginx/sites-available/superlists.ml \
    /etc/nginx/sites-enabled/superlists.ml
```

Systemd cofig 파일도 `sed`로 생성한다.

```sh
webapp@server: cat ./deploy_tools/gunicorn-systemd.template.service \
    | sed "s/DOMAIN/superlists.ml/g" \
    | sudo tee /etc/systemd/system/gunicorn-superlists.ml.service
```

두 서비스를 실행한다.


그리고 도메인 명으로 브라우저 접속을 해보면 앱이 잘 작동함을 확인한다.

![브라우저 실행](https://www.obeythetestinggoat.com/book/images/twp2_1101.png)

```sh
webapp@server:$ sudo systemctl daemon-reload
webapp@server:$ sudo systemctl reload nginx
webapp@server:$ sudo systemctl enable gunicorn-superlists.ml
webapp@server:$ sudo systemctl start gunicorn-superlists.ml
```
https://www.obeythetestinggoat.com/book/images/twp2_1101.png

잘 배포됨을 확인하고 fabfile.py 내용을 git repo에 저장하자.

```sh
$ git add deploy_tools/fabfile.py
$ git commit -m "Add a fabfile for automated deploys"
```

### Git 태그 릴리즈

현재 서버에 반영된 코드베이스가 어떤 것임을 표시하기 위해 git tag를 이용한다.

```sh
$ git tag LIVE
$ export TAG=$(date +DEPLOYED-%F/%H%M)  # this generates a timestamp
$ echo $TAG # should show "DEPLOYED-" and then the timestamp
$ git tag $TAG
$ git push origin LIVE $TAG # pushes the tags up
```

이렇게 하면 언제든지 현재 서버에 적용된 코드 베이스를 쉽게 확인할 수 있다.

tag가 적용되었는지 `git log` 로 확인해보자.

```sh
$ git log --graph --oneline --decorate
[...]
```
