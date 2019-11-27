# 2장 unittest 모듈을 이용한 기능 테스트 확장

## 앞으로 나아갈 방향

To-Do 웹 에플리케이션 개발

왜 선택했는가?
- 최소한의 실현 가능한(MinimumViableProduct) 예제로 적합
- 어떤 형태로든 확장이 가능하다.(마감일, 알람, 공유 기능 등..)
- 웹 프로그래밍 전반적인 내용과 TDD 를 배울 수 있음

## 기능 테스트

- 사용자 관점의 테스트
- 특정 기능을 사용자가 어떻게 사용하며 이때 애플리케이션이 어떻게 반응하는지 확인하는 방식
- Functional Test == Acceptance Test == End to End Test
- 사람이 이해할수 있는 스토리를 가지고 있어야 함
- 테스트 코드에 스토리를 주석으로 기록하여 먼저 작성 가능하다.

맨 마지막의 스토리를 주석으로 먼저 작성하는 방식은 좀 신선하다.

[02-01/functional_test.py](./02-01/functional_test.py)

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
