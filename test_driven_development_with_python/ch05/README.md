# 5장 사용자 입력 저장하기

## Intro

다시 한번 강조! TDD의 핵심은 **한 번에 한가지만 하는 것**

기능 테스트에 최소한의 기능만 구현

이번장에서 보여줄 것은?

- 사용자가 입력한 작업 아이템을 서버로 보내고 이를 저장한 후 다시 사용자에게 보여주는 시스템
- TDD 가 어떻게 반복적인 개발 스타일을 지원하는지 => 가장 빠른 방법은 아니나 결과적으로 개발 속도를 높여줌.
- 장고 모델, POST 요청처리, 장고 템플릿 테그 같은새로운 개념 소개

## POST 요청을 전송하기 위한 폼(Form) 연동(예제 : [05-01](05-01))

4장 마지막에서 하지못했던 사용자 입력 기능을 구현해보도록 한다. 

바로 아래 기능 테스트 부분이다.

```py
        # 그녀는 바로 작업을 추가하기로 한다.
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            '작업 아이템 입력'
            )

        # "공작깃털 사기" 라고 텍스트 상자에 입력한다.
        # (에디스의 취미는 날치 잡이용 그물을 만드는 것이다)
        inputbox.send_keys('공작깃털 사기')

        # 엔터키를 치면 페이지가 갱신되고 작업 목록에
        # "1: 공작깃털 사기" 아이템이 추가된다
        inputbox.send_keys(Keys.ENTER)

        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertTrue(
            any(row.text == '1: 공작깃털 사기' for row in rows),
            '신규 작업이 테이블에 표시되지 않는다'
            )
```

브라우저가 POST 요청을 보내기 위해서는

  - `<input\>` 속성에 name= 속성을 지정
  - `<form>` 테그로 감싸야 함
  - `<form>` 테그에 method="POST" 지정해서 전송 방식 설정

이 내용을 반영한 내용이 아래에 링크되어 있다.

[lists/templates/home.html](05-01/superlists/lists/templates/home.html)

이제 반영이 되었으니 기능 테스트를 돌려본다.

```sh
$ python functional_test.py
E
======================================================================
ERROR: test_can_start_a_list_and_retrieve_it_later (__main__.NewVisitorTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "functional_test.py", line 39, in test_can_start_a_list_and_retrieve_it_later
    table = self.browser.find_element_by_id('id_list_table')
  File "/Users/pilhwankim/.pyenv/versions/tdd-with-python-env/lib/python3.7/site-packages/selenium/webdriver/remote/webdriver.py", line 360, in find_element_by_id
    return self.find_element(by=By.ID, value=id_)
  File "/Users/pilhwankim/.pyenv/versions/tdd-with-python-env/lib/python3.7/site-packages/selenium/webdriver/remote/webdriver.py", line 978, in find_element
    'value': value})['value']
  File "/Users/pilhwankim/.pyenv/versions/tdd-with-python-env/lib/python3.7/site-packages/selenium/webdriver/remote/webdriver.py", line 321, in execute
    self.error_handler.check_response(response)
  File "/Users/pilhwankim/.pyenv/versions/tdd-with-python-env/lib/python3.7/site-packages/selenium/webdriver/remote/errorhandler.py", line 242, in check_response
    raise exception_class(message, screen, stacktrace)
selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: {"method":"css selector","selector":"[id="id_list_table"]"}
  (Session info: chrome=78.0.3904.108)


----------------------------------------------------------------------
Ran 1 test in 7.253s

FAILED (errors=1)
```

이전에 보지 못했던 몇가지 특이한 에러(그리고 현상)들이 나온다.

이 에러들을 파악해보려면 몇가지 디버깅 방법이 있다.

- print 문을 이용해 현재 페이지 텍스트 확인하기
- 에러 메시지를 개선해서 더 자세한 정보를 출력하기
- 수동으로 사이트를 열어보기
- time.sleep을 이용해 실행중에 있는 테스트를 잠시 정지시키기

여기서 마지막 sleep을 사용해보도록 한다.

[functional_test.py - sleep 추가](./05-01/functional_test.py)

기능 테스트를 다시 실행하면 브라우저가 10초 정도 멈추게 되는데 다음과 같은 화면이 나온다.

![TF 결과](./05-01.png)

장고는 CSRF 보호를 기본으로 지원한다. CSRF에 대해서는 [CSRF 란?](https://ko.wikipedia.org/wiki/%EC%82%AC%EC%9D%B4%ED%8A%B8_%EA%B0%84_%EC%9A%94%EC%B2%AD_%EC%9C%84%EC%A1%B0) 을 참고하자.

CSRF 보호를 위해 장고는 각 폼이 생성하는 POST 요청에 토큰을 부여한다.

현재 방금 form에 그 처리가 되어 있지 않아 이 에러가 `CSRF validation fail` 이 발생한 것이다.

장고는 이 기능도 간편하게 제공한다. CSRF 전용 **템플릿 테그**를 추가한다.

[lists/templates/home.html](05-01/superlists/lists/templates/home.html)

장고 내부에서는 이 테그를 CSRF 토근을 포함하는 `<input type="hidden">` 요소로 변경해서 랜더링한다.

다시 기능 테스트를 돌려보면 브라우저의 CSRF 에러는 나오지 않는다.

하지만 테스트 결과는 Fail 이 된다.

```sh
$ python functional_test.py
F
======================================================================
FAIL: test_can_start_a_list_and_retrieve_it_later (__main__.NewVisitorTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "functional_test.py", line 47, in test_can_start_a_list_and_retrieve_it_later
    '신규 작업이 테이블에 표시되지 않는다'
AssertionError: False is not true : 신규 작업이 테이블에 표시되지 않는다

----------------------------------------------------------------------
Ran 1 test in 16.030s

FAILED (failures=1)
```

이제 브라우저 동작을 확인했으니 time.sleep은 필요없으므로 제거하자.
