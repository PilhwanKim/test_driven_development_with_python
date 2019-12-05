# 4장 왜 테스트를 하는 것인가(그리고 리펙토링)?

## 프로그래밍은 우물에서 물을 퍼 올리는 것과 같다

- 켄트 벡(Kent Back, TDD) says
  - 우물가에 있는 물 뜨는 두레박 비유
  - 처음 몇번은 두레박으로 물을 퍼올리는건 쉬움
  - 시간이 지나면서 곧 지치기 시작함
  - **도르레** 를 이용하면 직접 퍼올리는 것보도 효율적
- TDD는 **도르레** 와 같이 작업 효율을 올려줌, 작업이 뒤로 미끄러져 가는것도 막아줌
- TDD는 **훈련** 이다. 자연스럽게 익혀지는 것이 아니다. 성과가 즉시 나는 것이 아닌 오랜 기간을 거쳐야 한다.
- 필자가 보여주고자 하는 것은 철저한 TDD. 무술의 카타[kata](https://en.wikipedia.org/wiki/Kata)와 같음
- 결론은 개발 내공증진에 분명 도움되니 무술처럼 연습해서 익혀라!

## 셀레늄을 이용한 사용자 반응 테스트(예제 : 04-01)

이전 장 마지막에 이어서 작업한다.

바로 아래 주석 처리되어 있는 내용의 테스트 코드를 작성한다.

```py
        # 그녀는 바로 작업을 추가하기로 한다.

        # "공작깃털 사기" 라고 텍스트 상자에 입력한다.
        # (에디스의 취미는 날치 잡이용 그물을 만드는 것이다)

        # 엔터키를 치면 페이지가 갱신되고 작업 목록에
        # "1: 공작깃털 사기" 아이템이 추가된다
```

[functional_test.py - 추가 작성한 테스트 코드](04-01/functional_test.py)

- 셀레늄 메소드 설명
  - find_element(s)_by_id - tag id로 요소를 찾음. 's'는 복수개의 요소를 list로 반환
  - find_element_by_tag_name - tag 이름으로 요소를 찾음. 's'는 복수개의 요소를 list로 반환
  - send_keys : 입력 요소를 타이핑함.

작성한 FT를 실행해보면 의도된 실패가 발생한다.

```sh
$ python functional_test.py

======================================================================
ERROR: test_can_start_a_list_and_retrieve_it_later (__main__.NewVisitorTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "functional_test.py", line 21, in test_can_start_a_list_and_retrieve_it_later
    header_text = self.browser.find_element_by_tag_name('h1').text
  File "/tdd-with-python-env/lib/python3.7/site-packages/selenium/webdriver/remote/webdriver.py", line 530, in find_element_by_tag_name
    return self.find_element(by=By.TAG_NAME, value=name)
  File "/tdd-with-python-env/lib/python3.7/site-packages/selenium/webdriver/remote/webdriver.py", line 978, in find_element
    'value': value})['value']
  File "/tdd-with-python-env/lib/python3.7/site-packages/selenium/webdriver/remote/webdriver.py", line 321, in execute
    self.error_handler.check_response(response)
  File "/tdd-with-python-env/lib/python3.7/site-packages/selenium/webdriver/remote/errorhandler.py", line 242, in check_response
    raise exception_class(message, screen, stacktrace)
selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: {"method":"css selector","selector":"h1"}
  (Session info: chrome=78.0.3904.108)

----------------------------------------------------------------------
Ran 1 test in 7.356s

FAILED (errors=1)
```
