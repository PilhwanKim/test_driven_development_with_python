# 7장 멋있게 만들기: 레이아웃, 스타일링, 테스트

## 이번장에서 다루는 것

- 기본 css 방법
- 부트스트랩 프레임워크와 통합
- 장고의 static file 이 어떻게 동작하고 테스트 하는 방법

## 레이아웃과 스타일을 기능적으로 테스트하기(예제 : [07-01](./07-01))

좀 더 사이트를 멋지게 만들어보자. 그러려면 다음 2가지를 해야 한다.

- 신규 및 기존 목록 추가를 위한 크고 멋있는 입력 필드
- 크고 시선을 끄는 중앙 입력 박스

먼저 메인 입력상자가 각 페이지에 제대로 배치되는지 간단히 확인하는 테스트 부터 시작한다.

기능 테스트에 새로운 메소드를 추가한다.

### [functional_tests/tests.py](./07-01/superlists/functional_tests/tests.py)

```py

[...]
    def test_layout_and_styling(self):
        # 에디스는 메인 페이지를 방문한다
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # 그녀는 입력 상자가 가운데 배치된 것을 본다
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size('width') / 2,
            512,
            delta=10
        )
```

- 창 크기 고정시키고 있음
- input 요소가 페이지 중앙에 위치하는지 계산함. 오차범위 +-10 픽셀 내로 있으면 통과

기능 테스트를 실행해 보면...

```sh
$ python manage.py test functional_tests

======================================================================
FAIL: test_layout_and_styling (functional_tests.tests.NewVisitorTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/pilhwankim/Github/books/test_driven_development_with_python/ch07/07-01/superlists/functional_tests/tests.py", line 105, in test_layout_and_styling
    delta=10
AssertionError: 64.0 != 512 within 10 delta (448.0 difference)
```

예상된 실패가 일어난다. 당분간 편법(!)을 사용하여 우회 통과하도록 하자.

### [lists/templates/home.html](./07-01/superlists/lists/templates/home.html)

```html
        <form method="POST" action="/lists/new">
+            <p style="text-align: center">
+                <input name="item_text" id="id_new_item" placeholder="작업 아이템 입력">
+            </p>
-            <input name="item_text" id="id_new_item" placeholder="작업 아이템 입력">
            {% csrf_token %}
        </form>
```

변경하면 일단 FT는 통과한다.

```sh
$ python manage.py test functional_tests
Ran 2 tests in 13.215s

OK
```

신규 작업 목록 페이지에서도 입력 상자가 가운데 배치되는지 확인하는 것도 추가하자.

### [functional_tests/tests.py](./07-01/superlists/functional_tests/tests.py)

```py
        # 그녀는 새로운 리스트를 시작하고 입력 상자가
        # 가운데 배치된 것을 확인한다.
        inputbox.send_keys('testing')
        inputbox.send_keys(Keys.ENTER)
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )
```

예상대로 또 다른 에러가 나온다.

```sh
AssertionError: 64.0 != 512 within 10 delta (448.0 difference)
```

이렇게 편법으로는 이제 통하지 않는다는 생각이 들 것이다.

편법으로 설계된 `<p style="tex-align: center">` 는 다시 원상복귀 한다.

## 멋있게 만들기: CSS 프레임워크 이용(예제 : [07-02](./07-02))

- 웹 페이지 디자인에 문외한인 개발자들의 대안 = CSS 프레임워크
- 부트스트랩(Bootstrap) = 가장 많이 사용

바로 적용해 보자. (최대한 책과 동일환경 동작하게 3버전을 사용)

```sh
$ wget -O bootstrap.zip https://github.com/twbs/bootstrap/releases/download/v3.3.2/bootstrap-3.3.2-dist.zip
$ unzip bootstrap.zip
$ mkdir lists/static
$ mv bootstrap-3.3.2-dist lists/static/bootstrap
$ rm bootstrap.zip
```

작업후 폴더는 다음과 같이 위치해야 한다.

```sh
lists
├── __init__.py
├── admin.py
├── apps.py
├── migrations
│   ├── 0001_initial.py
│   ├── 0002_item_text.py
│   ├── 0003_list.py
│   ├── 0004_item_list.py
│   └── __init__.py
├── models.py
├── static
│   └── bootstrap
│       ├── css
│       │   ├── bootstrap-theme.css
│       │   ├── bootstrap-theme.css.map
│       │   ├── bootstrap-theme.min.css
│       │   ├── bootstrap.css
│       │   ├── bootstrap.css.map
│       │   └── bootstrap.min.css
│       ├── fonts
│       │   ├── glyphicons-halflings-regular.eot
│       │   ├── glyphicons-halflings-regular.svg
│       │   ├── glyphicons-halflings-regular.ttf
│       │   ├── glyphicons-halflings-regular.woff
│       │   └── glyphicons-halflings-regular.woff2
│       └── js
│           ├── bootstrap.js
│           ├── bootstrap.min.js
│           └── npm.js
├── templates
│   ├── home.html
│   └── list.html
├── tests.py
├── urls.py
└── views.py
```

부트스트랩의 [온라인 공식 문서](http://bootstrapk.com/getting-started/#template)에 따라, HTML 템플릿에 다음과 같이 적용 가능하다.

```html
<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- 위 3개의 메타 태그는 *반드시* head 태그의 처음에 와야합니다; 어떤 다른 콘텐츠들은 반드시 이 태그들 *다음에* 와야 합니다 -->
    <title>부트스트랩 101 템플릿</title>

    <!-- 부트스트랩 -->
    <link href="css/bootstrap.min.css" rel="stylesheet">

    <!-- IE8 에서 HTML5 요소와 미디어 쿼리를 위한 HTML5 shim 와 Respond.js -->
    <!-- WARNING: Respond.js 는 당신이 file:// 을 통해 페이지를 볼 때는 동작하지 않습니다. -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <h1>Hello, world!</h1>

    <!-- jQuery (부트스트랩의 자바스크립트 플러그인을 위해 필요합니다) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
    <!-- 모든 컴파일된 플러그인을 포함합니다 (아래), 원하지 않는다면 필요한 각각의 파일을 포함하세요 -->
    <script src="js/bootstrap.min.js"></script>
  </body>
</html>
```

이 프로젝트에 이미 두개의 HTML 템플릿을 가지고 있어서 각각 템플릿에 적용해야 한다.

하지만 이러한 중복은 `Don't Repeat Yourself` 규칙에 위배된다.

다행히 장고는 이런 템플릿 중복 문제해결 방안이 있다 - 템플릿 상속

## Django 템플릿 상속 (예제 : [07-03](./07-03))

`home.html` 과 `list.html` 템플릿은 같은(중복된) 내용이 많다.

```sh
$ diff lists/templates/home.html lists/templates/list.html
7,10c7,8
<         <form method="POST" action="/lists/new">
<             <p style="text-align: center">
<                 <input name="item_text" id="id_new_item" placeholder="작업 아이템 입력">
<             </p>
---
>         <form method="POST" action="/lists/{{ list.id }}/add_item">
>             <input name="item_text" id="id_new_item" placeholder="작업 아이템 입력">
12a11,16
>
>         <table id="id_list_table">
>             {% for item in list.item_set.all %}
>                 <tr><td>{{forloop.counter}}: {{ item.text }}</td></tr>
>             {% endfor %}
>         </table>
```

두 템플릿의 다른점은

- form 이 다른 url 사용
- list.html 은 table 요소가 포함

이렇듯 다른점은 분리하고 공통점은 하나로 합치는 작업이 필요하다.

먼저 공통 템플릿을 작성해보자. 먼저 기존 템플릿을 복사한다.

```sh
$ cp lists/templates/home.html lists/templates/base.html
```

여기다 자식 템플릿이 들어갈 장소를 뜻하는 `blocks` 를 설정한다.

### [lists/templates/base.html](./07-03/superlists/lists/templates/base.html)

```html
<html>
    <head>
        <title>To-Do lists</title>
    </head>
    <body>
        <h1>{% block header_text %} {% endblock %}</h1>
        <form method="POST" action="{% block form_action %} {% endblock %}">
            <p style="text-align: center">
                <input name="item_text" id="id_new_item" placeholder="작업 아이템 입력">
            </p>
            {% csrf_token %}
        </form>
        {% block table %}
        {% endblock %}
    </body>
</html>
```

이제 공통영역은 base.html 에서 담당한다.

자식 템플릿(list.html, home.html) 은 blocks 에 해당하는 영역만 채우도록 변경한다.

### [lists/templates/home.html](./07-03/superlists/lists/templates/home.html)

```html
{% extends 'base.html' %}

{% block header_text %}To-Do{% endblock %}

{% block form_action %}/lists/new{% endblock %}
```

### [lists/templates/list.html](./07-03/superlists/lists/templates/list.html)

```html
{% extends 'base.html' %}

{% block header_text %}Your To-Do lists{% endblock %}

{% block form_action %}/lists/{{ list.id }}/add_item{% endblock %}

{% block table %}
    <table id="id_list_table">
        {% for item in list.item_set.all %}
            <tr><td>{{forloop.counter}}: {{ item.text }}</td></tr>
        {% endfor %}
    </table>
{% endblock %}
```

이제 변경한 내용이 잘 작동하는지 기능 테스트를 돌려서 확인하자.

```sh
$ python manage.py test functional_tests

AssertionError: 64.0 != 512 within 10 delta (448.0 difference)
```

여전히 실패는 남았으나 이전에도 있던 실패이므로 템플릿 리팩토링은 성공했다.
