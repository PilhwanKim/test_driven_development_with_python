# 파이썬을 이용한 클린 코드를 위한 테스트 주도 개발

## 설치

pyenv-virtualenv, direnv 가 설치되어 있다는 가정하에 시작

```sh
# python 3.7 설치
pyenv install 3.7.4

# virtualenv 환경 생성
pyenv virtualenv 3.7.4 tdd-with-python-env

# .envrc 등록
echo "source activate tdd-with-python-env" > .envrc

# 현재 디렉토리를 direnv 경로 등록
direnv allow

# pip 로 pypi 패키지 설치
pip install -r requirements.txt
```

### 참고 글

* pyenv-virtualenv 설치 1 : https://www.44bits.io/ko/post/direnv_for_managing_directory_environment

* pyenv-virtualenv 설치 2 : http://taewan.kim/post/python_virtual_env/

## 1부 TDD와 Django 개요

[1장 기능 테스트를 이용한 Django 설치](./ch01_Getting_Django_Set_Up_Using_a_Functional_Test/README.md)

## 2부 웹 개발 핵심편

## 3부 고급편

## 부록 테스트 고트님께 복종하라
