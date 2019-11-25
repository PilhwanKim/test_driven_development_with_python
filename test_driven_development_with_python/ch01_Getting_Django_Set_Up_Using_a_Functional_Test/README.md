# 1장 기능 테스트를 이용한 Django 설치

## Testing Goat

- 염소가 소리친다. "테스트를 먼저 해! 테스트를 먼저 하라고!"
- 사실 개발할 때는 잠시 테스트가 생각이 나지만 귀차니즘 + 시간부족에 초조함 등의 복합적인 생각이 들어 실천하지 않는 경우가 많다.
- 먼저 테스트를 작성한 후 실행 -> 예상대로 실패하는지 확인 -> 실제 코드 작성 ->  테스트 작성 2 -> (무한 반복...)
- 염소는 1번에 1가지만 행동 함.

## 실전 - Django를 이용한 애플리케이션 개발

[functional_test.py](./01/functional_test.py)

- 첫 단계 : Django가 제대로 설치되었는지 확인
  - Django 개발 서버 가동
  - 서버에 있는 웹 페이지 로컬 PC상의 브라우저 접속(셀레늄 브라우저 자동화 툴)

실행하면 어떻게 될까?

```sh
$ python3 functional_test.py
Traceback (most recent call last):
  File "functional_test.py", line 1, in <module>
    from selenium import webdriver
ModuleNotFoundError: No module named 'selenium'
```

- 예상대로 안된다. 이제 이걸 되게 해야한다.
