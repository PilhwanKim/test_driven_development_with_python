# 2장 unittest 모듈을 이용한 기능 테스트 확장

## 앞으로 나아갈 방향

To-Do 웹 에플리케이션 개발

왜 선택했는가?

- 최소한의 실현 가능한(MinimumViableProduct) 예제로 적합
- 어떤 형태로든 확장이 가능하다.(마감일, 알람, 공유 기능 등..)
- 웹 프로그래밍 전반적인 내용과 TDD 를 배울 수 있음

## 기능 테스트(예제 : [02-01](./02-01))

### 기능 테스트란 무엇인가?

- 사용자 관점의 테스트
- 특정 기능을 사용자가 어떻게 사용하며 이때 애플리케이션이 어떻게 반응하는지 확인하는 방식
- Functional Test == Acceptance Test == End to End Test
- 사람이 이해할수 있는 스토리를 가지고 있어야 함
- 테스트 코드에 스토리를 주석으로 기록하여 먼저 작성 가능하다.

맨 마지막의 스토리를 주석으로 먼저 작성하는 방식은 좀 신선하다.

### [functional_test.py - 스토리 주석이 추가](./02-01/functional_test.py)

```py
from selenium import webdriver

browser = webdriver.Chrome('chromedriver')

# 에디스(Edith)는 멋진 작업 목록 온라인 앱이 나왔다는 소식을 듣고
# 해당 웹 사이트를 확인하러 간다.
browser.get('http://localhost:8000')

# 웹 페이지 타이틀과 헤더가 'To-Do'를 표시하고 있다.
assert 'To-Do' in browser.title

# 그녀는 바로 작업을 추가하기로 한다.

# "공작깃털 사기" 라고 텍스트 상자에 입력한다.
# (에디스의 취미는 날치 잡이용 그물을 만드는 것이다)

# 엔터키를 치면 페이지가 갱신되고 작업 목록에
# "1: 공작깃털 사기" 아이템이 추가된다

# 추가 아이템을 입력할 수 있는 여분의 텍스트 상자가 존재한다.
# 다시 "공작깃털을 이용해서 그물 만들기"라고 입력한다 (에디스는 매우 체계적인 사람이다)

# 페이지는 다시 갱신되고, 두 개 아이템이 목록에 보인다.
# 에디스는 사이트가 입력한 목록을 저장하고 있는지 궁금하다.
# 사이트는 그녀를 위한 특정 URL을 생성해준다.
# 이 때 URL에 대한 설명도 함께 제공된다

# 해당 URL에 접속하면 그녀가 만든 작업 목록이 그대로 있는 것을 확인할 수 있다.

# 만족하고 잠자리에 든다.

browser.quit()
```

실제 실행시켜 보면

```sh
# 먼저 파이썬 서버를 실행
$ cd superlists
$ python manage.py runserver

# FT(Functional Test) 실행
$ python functional_test.py
Traceback (most recent call last):
  File "functional_test.py", line 10, in <module>
    assert 'To-Do' in browser.title
AssertionError
```

아직 브라우저 타이틀을 변경한 적이 없어서 실패한다.

## unittest로 바꾸기(예제 : [02-02](./02-02))

### pure python 테스트 코드의 문제점

- assert 조건이 맞지 않을시 발생하는 **AssertionError** 메시지가 명시적으로 우리 기능의 무엇이 문제인지 알려주지 않음(단순 Exception 메시지)
- 열려있는 크롬 브라우저 창을 테스트 종료시에 닫아주려면 try/finally 처리 필요하나 테스트마다 반복되는 코드가 발생함
- 고로 이 모든걸 제공하는 unittest가 필요하다

### [functional_test.py - unittest 적용](./02-02/functional_test.py)

```py
import unittest
from selenium import webdriver


class NewVisitorTest(unittest.TestCase):
    
    def setUp(self):
        self.browser = webdriver.Chrome('chromedriver')
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
        # 에디스(Edith)는 멋진 작업 목록 온라인 앱이 나왔다는 소식을 듣고
        # 해당 웹 사이트를 확인하러 간다.
        self.browser.get('http://localhost:8000')
        [...]


if __name__ == '__main__':
    unittest.main(warnings='ignore')

```

- 모든 테스트는 **test_** 로 시작하는 명칭으로 된 메서드만 실행한다. 현재 코드는 test_can_start_a_list_and_retrieve_it_later 가 테스트 메서드다
- setUp/tearDown 메서드는 각 테스트 메서드의 시작전/후로 실행한다. 각 테스트에 공통된 전후처리를 할때 사용한다
- assert 대신에 TestCase 의 self.assert* 메서드로 결과 검증을 한다.
- self.fail 은 강제적으로 테스트 실패를 발생시켜 에러 메시지를 출력한다.
- if __name__ == '__main__': 은 다른 스크립트에 임포트되서 실행할 경우에는 실행되지 않는다. python 명령으로 실행될 시 실행된다. unittest.main() 은 테스트 실행자를 run 하는 코드이다. 또한 자동으로 파일내 test코드들을 찾아서 실행시켜 준다.

### FT 실행 결과

```sh
$ python functional_test.py

F
======================================================================
FAIL: test_can_start_a_list_and_retrieve_it_later (__main__.NewVisitorTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "functional_test.py", line 19, in test_can_start_a_list_and_retrieve_it_later
    assert 'To-Do' in self.browser.title
AssertionError

----------------------------------------------------------------------
Ran 1 test in 4.884s

FAILED (failures=1)
```
