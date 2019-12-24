# 6장 최소 동작 사이트 구축

## Intro

이번장에 남은 일들

- 기능 테스트 후 남은 흔적(data) 제거
- 시스템이 하나의 목록만 지원하는 문제

## 기능 테스트 내에서 테스트 격리(예제 : [06-01](./06-01))

고전적 테스트 문제. 기능 테스트를 실행할 때마다 앞 테스트의 목록 아이템이 DB 에 남아있어 다음 테스트 결과를 방해함

해결 방식

1. 자체적인 솔루션을 적용하여 FT에 기존 결과물을 정리하는 코드를 작성하는 것
2. Django 에 탑재된 LiveServerTestCase 클래스를 이용하는 것

### LiveServerTestCase 클래스 동작

1. 자동으로 테스트용 데이터 베이스 생성
2. 기능 테스트를 위한 개발 서버를 가동
3. manage.py test 명령으로 실행 가능함

두 가지 해결방식중 LiveServerTestCase를 기능 테스트에 적용해보도록 한다

먼저 functional_tests.py를 장고 functional_tests 앱의 tests.py 로 이동시키는 작업을 해 보자.

```sh
$ cd superlists
$ mkdir functional_tests
$ touch functional_tests/__init__.py
```

장고 앱 디렉토리(혹은 파이썬 패키지)를 생성후 기존 기능 테스트 코드를 tests.py로 옮긴다.

```sh
$ cd ..
$ git mv functional_test.py superlists/functional_tests/tests.py
$ git status
```

현재 프로젝트 구조는 다음과 같이 변했다.

![작업후의 프로젝트 구조](./ch06-01.png)

이제부터는 기능 테스트 실행은

`python functional_tests.py` 가 아니라 

`python manage.py test functional_tests` 로 실행한다.

NewVisitorTest도 LiveServerTestCase를 상속하도록 테스트 코드도 변경해야 한다.

### [functional_tests/tests.py](./06-01/superlists/functional_tests/tests.py)

```py
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class NewVisitorTest(LiveServerTestCase):
    
    def setUp(self):
   [...]
```

그리고 selenium 접속도 `localhost:8000` 대신에 LiveServerTestCase 제공하는 `self.live_server_url` 로 다시 세팅해야 한다.

```py
[...]
    def test_can_start_a_list_and_retrieve_it_later(self):
        # 에디스(Edith)는 멋진 작업 목록 온라인 앱이 나왔다는 소식을 듣고
        # 해당 웹 사이트를 확인하러 간다.
        self.browser.get(self.live_server_url)
        [...]
```

아래 부분도 없애도 된다. 테스트 실행을 장고 manage.py에서 대신하기 때문이다.

```py

if __name__ == '__main__':
    unittest.main(warnings='ignore')
```

변경이 다 되면 처음으로 바뀐 기능 테스트를 실행해 본다.

`python manage.py test functional_tests` 로 실행한다.

```sh
python manage.py test functional_tests
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
F
======================================================================
FAIL: test_can_start_a_list_and_retrieve_it_later (functional_tests.tests.NewVisitorTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/pilhwankim/Github/books/test_driven_development_with_python/ch06/06-01/superlists/functional_tests/tests.py", line 64, in test_can_start_a_list_and_retrieve_it_later
    self.fail('Finish the test!')
AssertionError: Finish the test!

----------------------------------------------------------------------
Ran 1 test in 7.799s

FAILED (failures=1)
Destroying test database for alias 'default'...
```

리펙터링 전과 같이 self.fail에 걸리며 통과 한다.

두번째 실행해보면 첫번째 실행한 목록이 남아있지 않은 것을 발견한다.

![두번째 실행시 첫번째 실행데이터가 없다](./ch06-02.png)

좋은 소식이 있다. 이제부터는 `manage.py test` 를 실행하면 기능 테스트와 단위 테스트 동시에 실행된다

```sh
$ python manage.py test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.......F
======================================================================
FAIL: test_can_start_a_list_and_retrieve_it_later (functional_tests.tests.NewVisitorTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/superlists/functional_tests/tests.py", line 64, in test_can_start_a_list_and_retrieve_it_later
    self.fail('Finish the test!')
AssertionError: Finish the test!

----------------------------------------------------------------------
Ran 8 tests in 7.119s

FAILED (failures=1)
Destroying test database for alias 'default'...
```

단위 테스트만 실행하려면 `python manage.py test lists`을 실행하면 된다.

```sh
$ python manage.py test lists
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.......
----------------------------------------------------------------------
Ran 7 tests in 0.018s

OK
Destroying test database for alias 'default'...
```
