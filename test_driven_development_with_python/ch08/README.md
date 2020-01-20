# 8장 스테이징 사이트를 이용한 배포 테스트

## 이번장에서 다루는 것

- 우리가 만든 사이트를 실제 운영 가능한 진짜 웹 서버에 배포하는 방법

### TDD와 배포시 주의가 필요한 사항

- 정적파일(css, javascript, image 등)
  - 제공을 위한 특스한 설정 필요

- 데이터베이스
  - 권한
  - 경로문제
  - 테스트 데이터 관리에 유의

- 의존관계
  - 연계된 패키지 설치
  - 패키지 버전 확인

### 해결책

- 실 운영 환경과 동일한 staging 사이트 마련. 배포 전에 제대로 동작하는지 확인
- 스테이징 사이트에 대해 기능 테스트를 실행할 수 있음
- virtualenv 로 파이썬 패키지 의존관계 관리
- 자동화, 자동화, 자동화 : 스크립트를 이용해 신규 버전 배포, 스테이징 운영 동시 배포하여 동일 상태 유지.

### 우리가 할일

1. 스테이징 서버에서 실행할 수 있도록 FT 수정
2. 서버를 구축하고 거기에 필요한 모든 소프트웨어 설치한다. 또한 스테이징과 운영 도메인이 이 서버를 가리키도록 설정한다.
3. git을 이용해서 코드를 서버에 업로드한다.
4. Django 개발 서버를 이용해서 스테이징 사이트에서 약식 버전의 사이트를 테스트한다.
5. Virtualenv 사용법을 배워서 서버에 있는 파이썬 의존 관계를 관리하도록 한다.
6. 과정을 진행하면서 항시 FT 를 실행한다. 이를 통해 단계별로 무엇이 동작하고, 무엇이 동작하지 않는지 확인한다.
7. Gunicorn, Upstart, 도메인 소켓 등을 이용하여 사이트를 운영 서버에 배포하기 위한 설정을 한다.
8. 설정이 정상적으로 동작하면 스크립트를 작성하여 수동으로 했던 작업을 자동화 하도록 한다. 이를 통해 사이트 배포를 자동화 할 수 있다.
9. 마지막으로, 동일 스크립트를 이용해서 운영 버전의 사이트를 실제 도메인에 배포하도록 한다.

## 항상 그렇듯이 테스트부터 시작 (예제 : [08-01](./08-01))

기능 테스트를 스테이징 사이트에서 실행되도록 하기

테스트 임시 서버가 실행되는 주소를 변경

### functional_tests/tests.py

```py
import sys

[...]
class NewVisitorTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]
                return
        super().setUpClass()
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url
            super().tearDownClass()
```

`LiveServerTestCase`의 제약사항 - 자체 테스트 서버에서 샤용한다고 가정. 그래서 다음 변경사항 생김

- `setUpClass` : `unittest` 제공. 전체 테스트 클래스 실행시 1번 먼저 실행. 전체 클래스에 테스트 설정 제공
- `sys.argv`에 있는 `liveserver`라는 커맨드라인 인수를 찾음
- 이 인수를 찾으면 `setUpClass` 를 건너뛰옥 스테이징 서버 URL을 `server_url` 변수에 저장

따라서 `self.live_server_url` -> `self.server_url` 로 변경

### functional_tests/tests.py

```py
@@ -19,7 +34,7 @@
     def test_can_start_a_list_and_retrieve_it_later(self):
         # 에디스(Edith)는 멋진 작업 목록 온라인 앱이 나왔다는 소식을 듣고
         # 해당 웹 사이트를 확인하러 간다.
-        self.browser.get(self.live_server_url)
+        self.browser.get(self.server_url)

         # 웹 페이지 타이틀과 헤더가 'To-Do'를 표시하고 있다.
         self.assertIn('To-Do', self.browser.title)
@@ -69,7 +84,7 @@

         # 프란시스가 홈페이지에 접속한다.
         # 에디스의 리스트는 보이지 않는다.
-        self.browser.get(self.live_server_url)
+        self.browser.get(self.server_url)
         page_text = self.browser.find_element_by_tag_name('body').text
         self.assertNotIn('공작깃털 사기', page_text)
         self.assertNotIn('공작깃털을 이용해서 그물 만들기', page_text)
@@ -94,7 +109,7 @@

     def test_layout_and_styling(self):
         # 에디스는 메인 페이지를 방문한다
-        self.browser.get(self.live_server_url)
+        self.browser.get(self.server_url)
         self.browser.set_window_size(1024, 768)

         # 그녀는 입력 상자가 가운데 배치된 것을 본다
```

다른 부분에서 사이드 이펙트가 있는지 FT 를 실행한다.

```sh
    if cls.server_url == cls.live_server_url
                                           ^
SyntaxError: invalid syntax
```

책의 예제 그대로 따라하면 에러가 났다. 이유는 Django 의 버전에 따른 구현 방식이 바뀌었다. 

책의 저자는 이 문제에 대한 응답을 아래에 남겨놨다.

https://groups.google.com/forum/#!topic/obey-the-testing-goat-book/pokPKQQB2J8

단순하다 `tearDownClass` 메서드를 지울 것!

```py
class NewVisitorTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]
                return
        super().setUpClass()
        cls.server_url = cls.live_server_url
```

다시 FT 를 실행해보면 잘 된다.

```sh
$ python manage.py test functional_tests
..
----------------------------------------------------------------------
Ran 2 tests in 17.007s
```

이제는 스테이징 서버 URL로 실행해보자.

```sh
$ python manage.py test functional_tests --liveserver=staging.ottg.eu:8000
usage: manage.py test [-h] [--noinput] [--failfast] [--testrunner TESTRUNNER]
                      [-t TOP_LEVEL] [-p PATTERN] [-k] [-r] [--debug-mode]
                      [-d] [--parallel [N]] [--tag TAGS]
                      [--exclude-tag EXCLUDE_TAGS] [--version] [-v {0,1,2,3}]
                      [--settings SETTINGS] [--pythonpath PYTHONPATH]
                      [--traceback] [--no-color] [--force-color]
                      [test_label [test_label ...]]
manage.py test: error: unrecognized arguments: --liveserver=staging.ottg.eu:8000
```

아예 옵션이 사라졌다! 이것도 검색해보면 장고 1.11 버전 이후로 `DJANGO_LIVE_TEST_SERVER_ADDRESS` 환경변수로 대체되었음을 알수 있었다.

https://docs.djangoproject.com/en/3.0/releases/1.11/#liveservertestcase-binds-to-port-zero

이대로는 근본적인 해결책을 찾아야 해서 저자는 어떻게 변경했는지 영문 공개 페이지를 확인했더니 내용이 상당히 바뀌어 있었다.

https://www.obeythetestinggoat.com/book/chapter_manual_deployment.html

변경했던 것들을 다시 되돌리고 아래와 같이 변경하자.

### [functional_tests/tests.py](./08-01/superlists/functional_tests/tests.py)

```py
import os

[...]
class NewVisitorTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('chromedriver')
        self.browser.implicitly_wait(3)
+        staging_server = os.environ.get('STAGING_SERVER')  
+        if staging_server:
+            self.live_server_url = 'http://' + staging_server  

```

다시 FT 를 실행해보면 잘 된다.

```sh
$ python manage.py test functional_tests
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..
----------------------------------------------------------------------
Ran 2 tests in 14.670s

OK
```

`--liveserver` 옵션 대신에 환경변수 `STAGING_SERVER` 로 주소를 지정하면 원하는 대로 의도적인 실패가 발생함을 확인 가능하다.

```sh
$ STAGING_SERVER=superlists-staging.ottg.eu python manage.py test functional_tests
FE
======================================================================
ERROR: test_layout_and_styling (functional_tests.tests.NewVisitorTest)
----------------------------------------------------------------------
selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: {"method":"css selector","selector":"[id="id_new_item"]"}
  (Session info: chrome=79.0.3945.117)

======================================================================
FAIL: test_can_start_a_list_and_retrieve_it_later (functional_tests.tests.NewVisitorTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/superlists/functional_tests/tests.py", line 29, in test_can_start_a_list_and_retrieve_it_later
    self.assertIn('To-Do', self.browser.title)
AssertionError: 'To-Do' not found in 'superlists-staging.ottg.eu'

----------------------------------------------------------------------
Ran 2 tests in 8.546s

FAILED (failures=1, errors=1)
```

## 도메인명 취득

이후 실습을 위해 꼭 취득하라고 권장하고 있다. 무료로 도메인을 얻을수 있는 곳도 있으니 실습용으로 하나 장만하자.

https://freenom.com

여기에서 나는 `pilhwnakim.tk` 도메인을 취득했으니 이 기준으로 진행하도록 한다.
