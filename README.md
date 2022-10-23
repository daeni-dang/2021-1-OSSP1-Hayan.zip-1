# 2021-1-OSSP1-Hayan.zip-1
2021 공개SW Hayan.zip팀<br>

## 암기 보조 프로그램 ##

### 팀원
  + 김가은 
  + 김건우 
  + 김다은 
  + 변은서 
  + 이시은 
  + 이태규 

----------------------------
### licenses
- sources: LICENSE_APACHE</br>
   key: apache-2.0</br>
- sources: LICENSE_GNU</br>
   key: gpl-3.0</br>

----------------------------
### 주제 소개
발표나 면접을 위한 **암기를 보조하는 프로그램**이다.
사용자에게 대본을 입력받은 후 음성인식을 진행한다. 대본과 음성을 특정 조건에 맞추어 비교하여 일치여부 판단하는 프로그램이다.

It is a program that aids memorization for presentations or interviews.
After receiving scripts from users, voice recognition is carried out. It is a program that compares scripts and voices to specific conditions to determine whether they match.

### 개발 동기
대부분의 사람들이 필연적으로 발표를 진행하게 되는 상황에 맞닥뜨리게 된다. 
하지만 대부분의 면접과 발표 상황 등에서는 준비한 대본이나 글을 직접 보면서 진행하기엔 어려운 경우가 많다.
또한, 대본을 숙지한뒤 비언어적인 표현들과 함께 발표하는 것이 효과적이다. 
이런 상황에서 대본을 암기하는데 어려움을 겪고 있는 많은 사람들에게 도움을 주고자 다음과 같은 **암기보조프로그램**을 구상하게 되었다.

Most people face a situation in which they inevitably proceed with the presentation.
However, in most interviews and presentations, it is often difficult to proceed while looking at the script or writing prepared.
Also, it is effective to read the script and present it with nonverbal expressions.
In order to help many people who have difficulty memorizing scripts in these situations, the following "memorization assistance" was devised.

----------------------------
### 프로젝트 구조
```bash
📂hayanzip
┣ 📂app
┃ ┣ 📂migrations
┃ ┃ ┗ 📜__init__.py
┃ ┣ 📂static
┃ ┃ ┗ 📂css
┃ ┃ ┃ ┗ 📜main.css
┃ ┣ 📂templates
┃ ┃ ┗ 📂app
┃ ┃ ┃ ┗ 📜main.html
┃ ┣ 📜admin.py
┃ ┣ 📜apps.py
┃ ┣ 📜models.py
┃ ┣ 📜tests.py
┃ ┣ 📜urls.py
┃ ┣ 📜views.py
┃ ┗ 📜__init__.py
┣ 📂hayanzip
┃ ┣ 📜asgi.py
┃ ┣ 📜settings.py
┃ ┣ 📜urls.py
┃ ┣ 📜wsgi.py
┃ ┗ 📜__init__.py
┣ 📜manage.py
┗ 📜__init__.py
```

----------------------------
### 개발 환경
<p>
  <img src = "https://shields.io/badge/logo-python-blue?logo=python">
  <img src = "https://shields.io/badge/logo-django-brown?logo=django&logoColor=brown">
</p>

### Open Source
<p>
  <img src = "https://shields.io/badge/python-enjeon-purple?logo=python&logoColor=purple">
  <img src = "https://shields.io/badge/python-jamo-green?logo=python&logoColor=green">
  <img src = "https://shields.io/badge/logo-webkit_speech_recognition-yellow?logo=google%20chrome&logoColor=yellow">
</p>

----------------------------

### 패키지 설치
    >> pip install eunjeon
    >> pip install django
    >> pip install jamo

----------------------------
### 사용 방법
![image](https://user-images.githubusercontent.com/80972215/122677606-00405500-d21e-11eb-9f1e-0814a7026367.png)
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[프로그램 화면]
1. 대본을 왼쪽 텍스트 박스에 넣는다.
2. <분석하기> 버튼을 누른다.
3. <암기시작>버튼을 누르고, 대본을 암기한다.
4. 이때, <대본 on/off>를 통해 대본을 숨길 수 있다.
5. 암기가 끝난 후, <원본보기>버튼을 눌러 대본과 암기한 내용을 비교한다.
<br>

1. Put the script in the left text box.
2. Press the <분석하기> button.
3. Press the <암기시작> button and memorize the script.
4. At this point, you can hide the script through <대본 on/off>.
5. After memorizing, click the <원본보기> button to compare the script with the memorized content.

----------------------------
### 제약사항
1. 한국어 문법상 옳은 문장을 입력한다.
2. 영어는 입력되지 않는다.
3. 모두 높임 표현으로 입력된다. 
<br>

1. Type the correct sentence in Korean grammar.
2. English is not entered.
3. All are entered as honorific.

----------------------------
### 프로그램 구조도
![image](https://user-images.githubusercontent.com/80972215/122677637-1cdc8d00-d21e-11eb-8527-787812a9fd79.png)
