# 11장 입력 유효성 검사 및 테스트 구조화

지금까지는 한개의 `functional_tests.py`, `tests.py` 로 태스트를 작성했다.

이후로 새로운 기능을 만들면 테스트가 늘어날 텐데 한 파일에 너무 많은 테스트가 있어서 찾기 힘들어진다.

그래서 테스트 코드를 여러개의 파일로 쪼개는 시간을 가진다.

그리고 또한 Generic wait helper 도 작성한다.

## 유효성 검사 FT에서 시작 : 빈 아이템 방지(예제 : [11-01](./11-01))

처음 몇 명의 사용자가 사이트를 사용하기 시작하면서 실수로 빈 목록 항목을 제출하거나 목록에 동일한 항목 2 개를 입력하는 등 목록을 엉망으로 만드는 실수를 발견한다.

이걸 방지하는 FT를 구상해보자.

### [/functional_tests/tests.py](./11-01/superlists/functional_tests/tests.py)

```sh
def test_cannot_add_empty_list_items(self):
    # 에디스는 메인 페이지에 접속해서 빈 아이템을 실수로 등록하려고 한다.
    # 입력 상자가 비어있는 상태에서 엔터키를 누른다.

    # 페이지가 새로 고침되고, 빈 아이템을 등록할 수 없다는
    # 에러 메시지가 표시된다

    # 다른 아이템을 입력하고 이번에는 정상 처리된다

    # 그녀는 고의적으로 다시 빈 아이템을 등록한다.

    # 리스트 페이지에 다시 에러 메시지가 표시된다.

    # 아이템을 입력하면 정상 동작한다.
    self.fail('write me!')
```

테스트 파일이 복잡해지기 시작했기에 테스트 파일을 몇 개로 나누기 시작하자.

원칙 : 1 테스트 파일에 하나의 테스트만 넣기

### 테스트 건너 뛰기

리펙터링 시에는 테스트가 모두 통과된 상태에서 진행하는 것이 좋음.

방금 고의적으로 실패하는 테스트를 작성했는데 `unittest` 의 `skip` 데코레이터를 이용해서 잠시 이 테스트를 꺼 두자.

```py

from unittest import skip
[...]
    @skip
    def test_cannot_add_empty_list_items(self):
```

테스트 실행시 이 테스트는 무시하도록 만든다. 테스트 실행하면 테스트가 통과됨을 알수 있다.

```sh
$ python manage.py test functional_tests
[...]
Ran 3 tests in 19.832s

OK
Destroying test database for alias 'default'...
```

### 레드, 그린, 리팩터 의 리팩터를 잊지 말자

TDD 의 문제가 되는 이유중 하나 코드 구조가 나빠지는 경향이 있다. 이유는 전체 시스템에 신경 쓰기보단 오로지 테스트가 통과되는 것에 초점을 맞추기 때문

설계 측면에서 TDD는 만병 통치약이 아니다. 방법론이 코드가 테스트를 통과하도록 하는것에 주안점이 있는 것만은 아니다. 설계를 개선하기 위해 리팩터링에 시간을 투자해야 한다는 것을 의미한다.

리팩터링의 최적의 아이디어는 바로 떠오르진 않는다. 몇주 혹은 몇달 지난후에 아이디어가 떠오르기도 한다. 지금 일을 멈추고 예전 코드를 리팩터링 해야하는 것일까?

케이스 1) 이번장의 시작과 같은 상황이라면 신규 FT는 skip 처리하고 바로 리팩터링을 시작할 수 있다.

케이스 2) 아직 변경 코드가 많이 남아있고 신규 FT는 fail 상태라면 기존 동작상태가 보장되지 않는다. 이때 리팩터링은 위험하다. 따라서 작업목록에 기록해두고 동작상태가 모두 통과 될때까지 기다린후 리팩터링 한다.

(결론)동작상태가 모두 통과되는 상태(all green)에서 리팩터링을 시도해야 한다.

### 기능 테스트를 여러 파일로 분할하기

#### 각 테스트를 개별 클래스로 나누기(예제 : [11-02](./11-02))

##### [/functional_tests/tests.py](./11-02/superlists/functional_tests/tests.py)

```py
class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        [...]
    def tearDown(self):
        [...]
    def wait_for_row_in_list_table(self, row_text):
        [...]


class NewVisitorTest(FunctionalTest):

    def test_can_start_a_list_for_one_user(self):
        [...]
    def test_multiple_users_can_start_lists_at_different_urls(self):
        [...]


class LayoutAndStylingTest(FunctionalTest):

    def test_layout_and_styling(self):
        [...]



class ItemValidationTest(FunctionalTest):

    @skip
    def test_cannot_add_empty_list_items(self):
        [...]
```

바뀐 FT를 실행해보자.

```sh
$ python manage.py test functional_tests
Ran 3 tests in 23.579s

OK
Destroying test database for alias 'default'...
```

한 단계씩 착실히 진행하는 것이 복잡한 작업을 수월하게 만든다.

#### 하나의 파일에 하나의 클래스가 담도록 나누기(예제 : [11-03](./11-03))

아래과 같이 원래 파일을 복사한다. 하나의 base 파일을 만들어 나머지 다른 파일들이 이 파일을 상속하게 한다.

```sh
$ git mv functional_tests/tests.py functional_tests/base.py
$ cp functional_tests/base.py functional_tests/test_simple_list_creation.py
$ cp functional_tests/base.py functional_tests/test_layout_and_styling.py
$ cp functional_tests/base.py functional_tests/test_list_item_validation.py
```

[/functional_tests/base.py](./11-03/superlists/functional_tests/base.py)

```py
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        [...]
    def tearDown(self):
        [...]
    def wait_for_row_in_list_table(self, row_text):
        [...]
```

[/functional_tests/test_simple_list_creation.py](./11-03/superlists/functional_tests/test_simple_list_creation.py)

```py
from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class NewVisitorTest(FunctionalTest):

    def test_can_start_a_list_for_one_user(self):
        [...]
    def test_multiple_users_can_start_lists_at_different_urls(self):
        [...]
```

[/functional_tests/test_layout_and_styling.py](./11-03/superlists/functional_tests/test_layout_and_styling.py)

```py
from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest


class LayoutAndStylingTest(FunctionalTest):
        [...]
```

[/functional_tests/test_list_item_validation.py](./11-03/superlists/functional_tests/test_list_item_validation.py)

```py
from selenium.webdriver.common.keys import Keys
from unittest import skip
from .base import FunctionalTest


class ItemValidationTest(FunctionalTest):

    @skip
    def test_cannot_add_empty_list_items(self):
        [...]
```

리팩토링이 끝났으면 functional_tests 를 실행해보자.


```sh
$ python manage.py test functional_tests
[...]
Ran 3 tests in 20.790s

OK
Destroying test database for alias 'default'...
```

정상동작되었고 리팩토링이 완료되었다.

### 개별 테스트 파일 실행

이제는 테스트 파일을 개별적으로 실행 가능하다.

```sh
$ python manage.py test functional_tests.test_list_item_validation
Ran 1 test in 2.526s

OK
Destroying test database for alias 'default'...
```

특정 테스트에만 관심이 있다면 필요없는 다른 테스트를 기다릴 필요 없이 이렇게 히면 된다.

### FT 에 살 붙이기(예제 : [11-04](./11-04))

이제 신규 유효성 테스트를 작성한다.

[/functional_tests/test_list_item_validation.py](./11-04/superlists/functional_tests/test_list_item_validation.py)

```py
class ItemValidationTest(FunctionalTest):
    @skip
    def test_cannot_add_empty_list_items(self):
        # 에디스는 메인 페이지에 접속해서 빈 아이템을 실수로 등록하려고 한다.
        # 입력 상자가 비어있는 상태에서 엔터키를 누른다.
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('id_new_item').send_keys(Keys.ENTER)

        # 페이지가 새로 고침되고, 빈 아이템을 등록할 수 없다는 
        # 에러 메시지가 표시된다
        self.assertEqual(
            self.browser.find_element_by_css_selector('.has-error').text,  
            "빈 아이템을 등록할 수 없습니다"  
        )

        # 다른 아이템을 입력하고 이번에는 정상 처리된다
        self.browser.find_element_by_id('id_new_item').send_keys('우유 사기')
        self.browser.find_element_by_id('id_new_item').send_keys(Keys.ENTER)
        self.check_for_row_in_list_table('1: 우유 사기')

        # 그녀는 고의적으로 다시 빈 아이템을 등록한다.
        self.browser.find_element_by_id('id_new_item').send_keys(Keys.ENTER)

        # 리스트 페이지에 다시 에러 메시지가 표시된다
        self.check_for_row_in_list_table('1: 우유 사기')
        self.assertEqual(
            self.browser.find_element_by_css_selector('.has-error').text,  
            "빈 아이템을 등록할 수 없습니다"  
        )

        # 아이템을 입력하면 정상 동작한다
        ​self.browser.find_element_by_id('id_new_item').send_keys('tea 만들기')
        ​self.browser.find_element_by_id('id_new_item').send_keys(Keys.ENTER)
        self.check_for_row_in_list_table('1: 우유 사기')
        ​self.check_for_row_in_list_table('2: tea 만들기')

```

- 부트스트랩 css class 인 `.has-error` 를 사용해서 에러 텍스트를 표시한다.
- 작업 아이템 등록이 동작하는지 확인하기 위해 `check_for_row_in_list_table` 헬퍼 함수를 재사용한다.

FT 결과를 확인해보자.

### 단위 테스트를 여러개 파일로 리팩터링 하기(예제 : [11-05](./11-05))

모델을 위한 신규 테스트를 추가하기 전에, 단위 테스트를 기능 테스트와 비슷한 형태로 정리하려고 한다.
테스트를 아예 별도의 디렉토리로 이동한다.

```sh
$ mkdir lists/tests
$ touch lists/tests/__init__.py
$ git mv lists/tests.py lists/tests/test_all.py
$ git status
$ git add lists/tests
$ python manage.py test lists
[...]
Ran 10 tests in 0.034s

OK
$ git commit -m "Move unit tests into a folder with single file"
```

이제 `tests_all.py` 를 두 파일로 만든다. 

- `test_view.py` 뷰 테스트 전용
- `test_models.py` 모델 전용

```sh
$ git mv lists/tests/test_all.py lists/tests/test_views.py
$ cp lists/tests/test_views.py lists/tests/test_models.py
```

각 파일에 필요한 테스트만 정리하자.

[/lists/tests/test_models.py](./11-05/superlists/lists/tests/test_models.py)
```py
from django.test import TestCase
from lists.models import Item, List


class ListAndItemModelsTest(TestCase):
        [...]
```

[/lists/tests/test_models.py](./11-05/superlists/lists/tests/test_views.py)

```py
--- a/lists/tests/test_views.py
+++ b/lists/tests/test_views.py
@@ -103,34 +104,3 @@ class ListViewTest(TestCase):
         self.assertNotContains(response, 'other list item 1')
         self.assertNotContains(response, 'other list item 2')

-
-
-class ListAndItemModelsTest(TestCase):
-
-    def test_saving_and_retrieving_items(self):
[...]
```

태스트를 실행해서 정상 동작하는지 확인한다.

```sh
$ python manage.py test lists
[...]
Ran 9 tests in 0.040s

OK
```
