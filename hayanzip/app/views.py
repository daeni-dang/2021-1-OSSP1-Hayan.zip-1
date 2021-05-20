#-*- coding:utf-8 -*-
import json

from django.http import HttpResponse
from django.shortcuts import render
from eunjeon import Mecab
import queue
import numpy as np

# Create your views here.
global script_table
global voice_table
global script_index
global q
global trueSentenceIndex
global falseSentenceIndex
global element_table
global modifier_table

script_table = []
voice_table = []
script_index = 0
q = queue.Queue()
trueSentenceIndex = []
falseSentenceIndex = []
element_table = np.empty((0, 9), dtype=list)
modifier_table = []
lastTrueIndex = -1
yellowSentenceIndex = []

def main(request):
    global script_table
    global voice_table
    global script_index
    global q
    global trueSentenceIndex  # trueSentence의 index 저장할 공간
    global lastTrueIndex
    global yellowSentenceIndex
    global falseSentenceIndex  # falseSentence의 index 저장할 공간
    global element_table
    global modifier_table


    mecab = Mecab()

    if request.method == 'POST':
        str = request.POST.get('final_str', None)
        if str == None:  # 대본 입력됐을 경우
            text = request.POST['inputStr']
            element_table = np.empty((0, 9), dtype=list)
            script_table = sentence_division(text) #형태소 포함된 배열
            script_string_array = sentence_without_part(text, script_table) #형태소 없는 배열
            script_index = 0
            trueSentenceIndex = []
            lastTrueIndex = -1
            yellowSentenceIndex = []
            falseSentenceIndex = []
            return render(request, 'app/main.html', {'text': text, 'script_string_array': script_string_array})
        else:
            mecab_result = mecab.pos(str)
            for i in range(len(mecab_result)):
                q.put(mecab_result[i][0])
                if is_sentence_End(mecab_result[i]):
                    print(mecab_result[i])
                    one_sentence = ""
                    for j in range(0, q.qsize()):
                        one_sentence += q.get()
                    voice_table = sentence_division(one_sentence)

                    for i in range(script_index-6, script_index+6): #앞 뒤 여섯 문장까지 검사
                        if i<0: #범위 벗어날 때 처리
                            continue
                        if i>=len(script_table): #범위 벗어날 때 처리
                            break
                        if i in trueSentenceIndex or i in yellowSentenceIndex: #이미 말한 문장에 있으면 다음 문장 검사
                            continue
                        if super_compare(i, voice_table[0], one_sentence): #맞는 문장 찾았다면 그만 검사
                            if lastTrueIndex>i:
                                yellowSentenceIndex.append(i)
                            else:
                                trueSentenceIndex.append(i)
                                lastTrueIndex=i
                            break

                    script_index += 1
            data = {    #Json으로 넘길 data 생성
                'trueSentenceIndex': trueSentenceIndex,
                'yellowSentenceIndex': yellowSentenceIndex,
                'falseSentenceIndex': falseSentenceIndex
            }
            return HttpResponse(json.dumps(data), content_type="application/json")

    return render(request, 'app/main.html')

def super_compare(script_index, voice_sentence, one_sentence):
    voice_sentence_component = make_element_table(voice_sentence, one_sentence)
    if simple_compare(script_table[script_index], voice_sentence):
        return True
    elif change_taxis_compare(element_table[script_index], voice_sentence_component, one_sentence):
        return True
    elif j_compare(element_table[script_index], voice_sentence_component):
        return True
    elif flag_true_compare(element_table[script_index], voice_sentence_component):
        return True
    else:
        return False

def simple_compare(script_sentence, voice_sentence):
    if len(script_sentence) != len(voice_sentence):
        return False
    for i in range(0,len(script_sentence)):
        if script_sentence[i][0] != voice_sentence[i][0]:
            return False
    return True

def change_taxis_compare(script_sentence_component, voice_sentence_component, origin_sentence):
    for i in range(0, 7):
        for j in range(0, len(script_sentence_component[i])):
            if voice_sentence_component[i]:
                if script_sentence_component[i][j][0] != voice_sentence_component[i][j][0]:
                    return False

    return True

# 시제와 부정 표현이 모두 일치하는지 확인하는 함수
def flag_true_compare(script_sentence_component, voice_sentence_component):
    # 7: 시제가 맞는지 확인
    # 8: 부정표현이 맞는지 확인
    if script_sentence_component[7] == voice_sentence_component[7] \
            and script_sentence_component[8] == voice_sentence_component[8]:
        return True
    else:
        return False


def add_space_after_mot(input_string):  # '못' 뒤에 띄어쓰기 추가하는 함수 : '못'을 기준으로 split한 후, 각 요소 사이에 '못+공백'을 추가하여 합침.
    split_neg = input_string.split('못')
    for i in range(len(split_neg)):
        string = '못 '.join(split_neg)
    return string

def j_compare(script_sentence_component, voice_sentence_component):
    for i in range(len(voice_sentence_component)):
         for j in range(len(voice_sentence_component[i])):
            print(voice_sentence_component[i][j], end=' ')
         print()
    for i in range(len(script_sentence_component)):
        for j in range(len(script_sentence_component[i])):
            print(script_sentence_component[i][j], end=' ')
        print()
    for q in range(0, 2):
        for k in range(0, len(script_sentence_component[q])):
            if voice_sentence_component[q]:
                print("script----------------")
                print(script_sentence_component[q][k][0])
                print("voice----------------")
                print(voice_sentence_component[q][k][0])
                if voice_sentence_component[q][k][1] == 'JX'or voice_sentence_component[q][k][1]=='JKS'or voice_sentence_component[q][k][1]=='JKO':
                    continue
                if script_sentence_component[q][k][0] != voice_sentence_component[q][k][0]:
                    print("False")
                    return False

    for i in range(2, 7):
        for j in range(0, len(script_sentence_component[i])):
            if voice_sentence_component[i]:
                print("script----------------")
                print(script_sentence_component[i][j][0])
                print("voice----------------")
                print(voice_sentence_component[i][j][0])
                if script_sentence_component[i][j][0] != voice_sentence_component[i][j][0]:
                    print ("False")
                    return False

    return True

def is_sentence_End(last_token):  # 문장의 마지막인지 판단 : EF[종결어미] 이거나 EC(연결어미)로 분석된 마지막 요소
    # find('str')는 str의 위치를 반환하는 함수. 없을 때는 -1 반환
    # 문장의 마지막 형태소일 때(즉, EF[종결어미]를 만났을 때)
    # 혹은 EC일 경우, '다','요','까'의 경우 종결어미로 인식
    if last_token[1].find('EF') != -1 \
            or last_token[1].find('EC') != -1:
        return True
    else:
        return False

def is_MAG_except_neg(token):  # '못', '안'을 제외한 MAG[일반 부사]인가 판단
    if token[1] == 'MAG':
        if token[0] != '못' and token[0] != '안':
            return True
    return False


def is_mark(token):  # 문장부호(. ? ! , · / : )인지 판단
    if token[1] == 'SF' or token[1] == 'SC':
        return True
    return False

# 찾고자 하는 문자('했' 같은 것)가 있는지 판단하는 함수
def is_have_char(what_find, token):
    if token[0].find(what_find) != -1:
        return True
    else:
        return False

# 찾고자 하는 태그('EF' 같은 것)가 있는지 판단하는 함수
def is_have_tag(what_find, token):
    if token[1].find(what_find) != -1:
        return True
    else:
        return False
def sentence_without_part2(text):   #연결어미로 끝나지 않을 때 포함하여 원본 반환
    mecab = Mecab()
    sentences=[]
    index=0
    mecab_text = mecab.pos(text)
    sentence = ''
    for i in range(0,len(mecab_text)):
        sentence = text
        if is_sentence_End(mecab_text[i]):
            index=text.find(mecab_text[i][0])
            index+=len(mecab_text[i][0])
            if(i<len(mecab_text)-1):
                if is_mark(mecab_text[i+1]):
                    index+=1
            sentence=text[:index]
            text=text[index:]
            sentences.append(sentence)

    if not (text.isspace()) and text!='':
        sentences.append(text)
    return sentences

def sentence_without_part(input_string, string_table):
    #형태소 구분 없이 문자열로만 string 문장 구분
    sentences=[]    #구분된 문장들 담을 배열
    for i in range(0,len(string_table)):
        sentence = ''   #한 문장 저장할 문자열
        for j in range(0, len(string_table[i])):
            if is_sentence_End(string_table[i][j]) :    #문장의 끝이라면
                index = input_string.find(string_table[i][j][0]) #문장의 끝 요소 index 찾음
                index += len(string_table[i][j][0]) #해당 문자까지 출력할 것이므로 그 문자의 길이만큼 index 증가
                if index < len(input_string):   #만약 마지막 요소가 아니라면
                    if input_string[index] == '.' or input_string[index] == ',':    #다음 요소가 .이나 ,일 때
                        index += 1; #해당 문자도 포함하기 위해 index 1 증가
                sentence=input_string[:index]  #처음부터 끝까지 문장 저장
                input_string=input_string[index:]   #저장한 문장은 제외
                break
        sentences.append(sentence)  #문장 추가
    return sentences


def sentence_division(input_string):
    global element_table

    mecab = Mecab()

    input_string = add_space_after_mot(input_string)  # '못' 뒤에 띄어쓰기 추가

    string_table = []  # 한 문장씩 저장할 테이블
    mecab_result = mecab.pos(input_string)  # ex) [('안녕', 'NNG'), ('하', 'XSV'), ('세요', 'EP+EF')]

    string_start = 0  # 각 문장의 첫번째 요소 가르키는 변수
    cnt = 0  # 한 문장에 대해 형태소 분석이 안 된 문장을 index로 찾아가기 위한 변수
    for i in range(len(mecab_result)):
        if is_sentence_End(mecab_result[i]):  # 문장의 마지막인지 판단
            sentence = []
            for j in range(string_start, i + 1):  # 한 문장 내의 첫번째 요소부터 마지막 요소까지 저장.
                # if is_MAG_except_neg(mecab_result[j]):  # '못', '안'을 제외한 MAG[일반 부사]는 저장 X
                #     continue
                if is_mark(mecab_result[j]):  # 문장부호는 저장 X
                    continue
                sentence.append(mecab_result[j])  # 각 요소를 현재 문장에 추가
            string_table.append(sentence)  # 완성된 한 문장을 테이블에 추가
            origin_string_table = sentence_without_part(input_string, string_table)  # 형태소 분석이 안 된 origin 문장을 찾아서 저장(관형어 찾는 함수에서 사용하기 위해)
            one_line_temp = make_element_table(sentence, origin_string_table[cnt])
            element_table = np.append(element_table, np.array([one_line_temp], dtype=list), axis=0)  # element_table 행 추가
            modifier_table.append(make_modifier_table(origin_string_table[cnt], sentence))  # modifier_table 행 추가
            cnt += 1
            string_start = i + 1  # 다음 문장의 첫 번째 요소를 가리킴.

    # element_table에 잘 들어갔는지 확인하기 위해 출력하는 코드
    # print("=================================")
    # for i in range(len(element_table)):
    #     for j in range(len(element_table[i])):
    #         print(element_table[i][j], end='  ')
    #     print()
    # print("=================================")

    # modifier_table에 잘 들어갔는지 확인하기 위해 출력하는 코드
    # print("=================================")
    # for i in range(len(modifier_table)):
    #     for j in range(len(modifier_table[i])):
    #         print(modifier_table[i][j], end='  ')
    #     print()
    # print("=================================")

    return string_table

    # sentence_division 함수를 한번 실행하면 total_table 완성! total_table은 global 변수 이므로 함수 실행 후 사용하면 됨!
    # 문제! : 다은이 -> 다(MAG) + 은이(NNG) : MAG 삭제


# 대본에 대해 문장별로 요소들을 정리하여 total_table에 담는 함수
# | 주어 | 목적어 | 서술어 | 관형어 | 부사어 | 보어 | 아무것도 아닌거 | 시제 flag | 부정의 의미인지 아닌지 flag |
# |  0  |   1   |   2   |   3   |   4   |  5  |      6       |    7     |            8             |
def make_element_table(mecab_sentence, origin_sentence):

    divide_line = [[], [], [], [], [], [], [], [], []]
    other_element = []

    divide_line[0].extend(find_s(mecab_sentence))
    divide_line[1].extend(find_o(mecab_sentence))
    divide_line[2].extend(find_verb(mecab_sentence))
    divide_line[3].extend(find_tubular(origin_sentence, mecab_sentence))
    divide_line[4].extend(find_adverb(mecab_sentence))
    divide_line[5].extend(find_complement(mecab_sentence))

    for i in range(len(mecab_sentence)):    # 각 언어 요소들 검사에 해당하지 않는 모든 요소들을 찾아냄
        flag = 0
        for j in range(len(divide_line) - 3):
            for k in range(len(divide_line[j])):
                if mecab_sentence[i] == divide_line[j][k]:
                    flag = 1
        if flag == 0:
            other_element.append(mecab_sentence[i])

    divide_line[6].extend(other_element)
    divide_line[7].extend(tense_to_flag(mecab_sentence))
    divide_line[8].extend(find_neg(mecab_sentence))

    return divide_line

# 체언을 꾸미는 말만 따로 모아놓는 테이블을 만드는 함수
def make_modifier_table(input_string, mecab_string):
    temp_string = mecab_string
    temp_modifier = []

    for i in range(len(temp_string)):
        modifier_line = [[], [], []]
        modifier_line_two = [[], []]
        if temp_string[i][1].find('ETM') != -1:  # 관형형 전성어미를 통해 관형어를 찾음
            if temp_string[i][1].find('+') != -1:  # 관형형 전성어미가 다른 형태소에 포함되어 나오는 경우(ex.('못생긴', 'VA+ETM'))
                inputIndex = input_string.find(temp_string[i][0])
                if temp_string[i - 1] == temp_string[len(temp_string) - 1]:  # 여러 개의 관형형 전성어미가 나올 경우 띄어쓰기로 각각을 구분하기 때문에 맨 앞의 관형형 전성어미에 대한 예외처리
                    modifier_line_two[0].extend(temp_string[i])
                    modifier_line_two[1].extend(temp_string[i + 1])
                    temp_modifier.append(modifier_line_two)

                elif input_string[inputIndex - 1] != ' ':  # 관형형 전성어미가 다른 형태소와 합성되어 있으며 그 앞에 다른 형태소가 나오는 경우 관형형 전성어미의 앞의 단어도 list에 추가(ex.('깨끗', 'XR'), ('한', 'XSA+ETM'))
                    modifier_line[0].extend(temp_string[i - 1])
                    modifier_line[1].extend(temp_string[i])
                    modifier_line[2].extend(temp_string[i + 1])
                    temp_modifier.append(modifier_line)

                else:  # 관형형 전성어미가 붙어서 한번에 나오는 경우 그 단어만 관형어 list에 추가(ex.('아름다운', 'VA+ETM'))
                    modifier_line_two[0].extend(temp_string[i])
                    modifier_line_two[1].extend(temp_string[i + 1])
                    temp_modifier.append(modifier_line_two)

            else:  # 관형형 전성어미가 다른 형태소에 포함되지 않고 나오는 경우(ex.('작', 'VA'), ('은', 'ETM'))
                modifier_line[0].extend(temp_string[i - 1])
                modifier_line[1].extend(temp_string[i])
                modifier_line[2].extend(temp_string[i + 1])
                temp_modifier.append(modifier_line)

    return temp_modifier

# 주어 찾는 함수
def find_s(sentence):
    s_table = []  # 주어들만 저장할 테이블
    for k in range(len(sentence)):  # 테이블에 저장된 한 문장 길이 동안
        if ((sentence[k][0] == '가' and sentence[k][1] == 'JKS') or (sentence[k][0] == '이' and sentence[k][1] == 'JKS')):
            # 가,이 중 주격 조사인 것들에 한해
            cnt = 0
            for m in range(0, k):  # 주격 조사 앞에 있는 것들중
                if (sentence[m][1] == 'NNG' or sentence[m][1] == 'NNP' or sentence[m][1] == 'NNB' or sentence[m][
                    1] == 'NP'):
                    # 명사에 해당 되는 것들 중에
                    cnt = m  # 가장 주격 조사에 가까운 것을
            s_table.append(sentence[cnt])  # 주어라고 저장
            s_table.append(sentence[k])  # 주어 뒤에 조사(확인용)

        if ((sentence[k][0] == '은' and sentence[k][1] == 'JX') or (sentence[k][0] == '는' and sentence[k][1] == 'JX')):
            # 은, 는 중 보조사 인것들에 한해
            jks_cnt = -1  # 주격조사count변수
            jx_cnt = -1
            for x in range(len(sentence)):  # 테이블의 i번째 문장 길이동안
                if (sentence[x][1] == 'JKS'):  # jsk(주격 조사가 있으면)
                    jks_cnt += 1  # count변수++
            for jx in range(0, k):
                if ((sentence[jx][0] == '은' and sentence[jx][1] == 'JX') or (
                        sentence[jx][0] == '는' and sentence[jx][1] == 'JX')):
                    jx_cnt += 1
            if (jks_cnt < 0 and jx_cnt < 0):  # 만약 주격 조사가 없으면
                for z in range(0, k):  # 은, 는 앞에 있는 것들중
                    N_cnt = 0
                    if (sentence[z][1] == 'NNG' or sentence[z][1] == 'NNP' or sentence[z][1] == 'NNB' or sentence[z][
                        1] == 'NP'):
                        # 명사에 해당 되는 것들 중에
                        N_cnt = z  # 가장 주격 조사에 가까운 것을

                s_table.append(sentence[N_cnt])  # 주어라고 저장
                s_table.append(sentence[k])  # 주어 뒤에 조사(확인용)

    return s_table

#목적어 찾는 함수
def find_o(sentence):
    cnt = 0
    o_table = []  # 목적어들만 저장할 테이블
    for k in range(len(sentence)):  # 문장 한문장 안에
        if ((sentence[k][0] == '을' and sentence[k][1] == 'JKO') or (sentence[k][0] == '를' and sentence[k][1] == 'JKO')):
            # 을를 인데 목적격 조사인 것이 나오면
            o_table.append(sentence[k - 1])  # 목적어 라고 저장
            o_table.append(sentence[k])  # 목적어 뒤에 조사(확인용)

        if ((sentence[k][0] == '은' and sentence[k][1] == 'JX') or (sentence[k][0] == '는' and sentence[k][1] == 'JX')):
            # 은 는 인데 보조사 인 경우
            jks_cnt = -1  # 주격조사를 count
            jx_cnt = -1
            for x in range(len(sentence)):  # 테이블의 i번째 문장 길이동안
                if (sentence[x][1] == 'JKS'):  # jsk(주격 조사가 있으면)
                    jks_cnt += 1  # count변수++
            for jx in range(0, k):
                if ((sentence[jx][0] == '은' and sentence[jx][1] == 'JX') or (
                        sentence[jx][0] == '는' and sentence[jx][1] == 'JX')):
                    jx_cnt += 1
            if (jks_cnt >= 0 or jx_cnt >= 0):  # 주격 조사가 있으면
                for z in range(0, k):  # 은, 는 앞에 있는 것들중
                    N_cnt = 0
                    if (sentence[z][1] == 'NNG' or sentence[z][1] == 'NNP' or sentence[z][1] == 'NNB' or sentence[z][
                        1] == 'NP'):
                        # 명사에 해당 되는 것들 중에
                        N_cnt = z  # 가장 주격 조사에 가까운 것을

                o_table.append(sentence[N_cnt])  # 조사 앞을 목적어라고 저장
                o_table.append(sentence[k])  # 목적어 뒤에 조사(확인용)

    return o_table

# 서술어를 찾는 함수
def find_verb(input_string):
    verb_table=[]
    start_flag = -1  # 서술어의 시작 플래그 초기화
    for j in range(0, len(input_string)):
        if start_flag == -1 and is_have_tag('V', input_string[j]):  # 문장 요소에 V가 있다면
            start_flag = j  # 시작 플래그는 현재 토큰 index
        elif is_have_tag('NNG', input_string[j]):  # 문장 요소에 N이 있다면
            start_flag = -1  # 서술어가 아니므로 start_flag = -1
    if start_flag != -1:  # start_flag가 -1이면 서술어가 없다는 것
        if start_flag > 0:  # start flag가 0이라면 앞에 것 볼 필요X
            if is_have_tag('NNG', input_string[start_flag - 1]):  # start_flag 앞의 토큰이 명사라면
                start_flag -= 1  # 시작 플래그를 하나 줄인다.
        for k in range(start_flag, len(input_string)):  # start_flag부터 끝까지 서술어
            verb_table.append(input_string[k])

    return verb_table

# 관형어를 찾는 함수 : 관형격 조사를 통해 관형어를 찾는 경우, 관형사를 관형어로 찾는 경우, 관형형 전성어미를 통해 관형어를 찾는 경우로 구성
def find_tubular(input_string, mecab_string):  # (체언 단독의 경우(ex.우연히 고향 친구를 만났다)와 체언의 자격을 가진 말 + 관형격 조사의 경우(ex.그는 웃기기의 천재다) 아직 처리 X)
    temp_string = mecab_string
    tubularArr = []

    for i in range(len(temp_string)):
        if temp_string[i][1].find('JKG') != -1:  # 관형격 조사를 통해 관형어를 찾음. 관형격 조사와 그 앞의 단어는 관형어이므로 이를 list에 추가
            tubularArr.append(temp_string[i - 1])
            tubularArr.append(temp_string[i])

        if temp_string[i][1].find('MM') != -1:  # 관형사를 관형어로 판단. 관형사를 list에 추가
            tubularArr.append(temp_string[i])

        if temp_string[i][1].find('ETM') != -1:  # 관형형 전성어미를 통해 관형어를 찾음
            if temp_string[i][1].find('+') != -1:  # 관형형 전성어미가 다른 형태소에 포함되어 나오는 경우(ex.('못생긴', 'VA+ETM'))
                inputIndex = input_string.find(temp_string[i][0])
                if temp_string[i - 1] == temp_string[
                    len(temp_string) - 1]:  # 여러 개의 관형형 전성어미가 나올 경우 띄어쓰기로 각각을 구분하기 때문에 맨 앞의 관형형 전성어미에 대한 예외처리
                    tubularArr.append(temp_string[i])
                elif input_string[inputIndex - 1] != ' ':  # 관형형 전성어미가 다른 형태소와 합성되어 있으며 그 앞에 다른 형태소가 나오는 경우 관형형 전성어미의 앞의 단어도 list에 추가(ex.('깨끗', 'XR'), ('한', 'XSA+ETM'))
                    tubularArr.append(temp_string[i - 1])
                    tubularArr.append(temp_string[i])
                else:  # 관형형 전성어미가 붙어서 한번에 나오는 경우 그 단어만 관형어 list에 추가(ex.('아름다운', 'VA+ETM'))
                    tubularArr.append(temp_string[i])
            else:  # 관형형 전성어미가 다른 형태소에 포함되지 않고 나오는 경우(ex.('작', 'VA'), ('은', 'ETM'))
                tubularArr.append(temp_string[i - 1])
                tubularArr.append(temp_string[i])

    return tubularArr  # 한 문장 안에 관형어는 여러 개가 될 수 있으므로 list의 형식으로 값을 반환

# 부사어를 찾는 함수
def find_adverb(input_string):
    temp_string = input_string
    adverbArr = []

    for i in range(len(temp_string)):
        if temp_string[i][1].find('MAG') != -1:
            adverbArr.append(temp_string[i])

        if temp_string[i][1].find('MAJ') != -1:
            adverbArr.append(temp_string[i])

        if temp_string[i][1].find('JKB') != -1:
            adverbArr.append(temp_string[i - 1])
            adverbArr.append(temp_string[i])

    return adverbArr

# 부정표현 flag

# 보어를 찾는 함수 : 보격 조사를 찾고 보격 조사 앞에 있는 단어 + 보격 조사를 보어로 반환
def find_complement(input_string):  # ('되다'의 경우 현재 보격 조사 판별 X)
    temp_string = input_string
    complementArr = []
    for i in range(len(temp_string)):
        if temp_string[i][1].find('JKC') != -1:  # 형태소 분석을 한 결과에서 보격 조사를 찾음
            complementArr.append(temp_string[i - 1])
            complementArr.append(temp_string[i])  # 보격 조사와 그 앞의 단어가 보어이므로 두 개 모두 list에 넣어줌
    return complementArr  # 한 문장 안에 보어가 여러 개가 될 수 있으므로 list의 형식으로 값을 반환

# 시제 찾는 함수
def find_tense(sentence):
    tense_table = [['past', ], ['present', ], ['future', ]] # 문자열과 시제를 함께 저장할 테이블
    # ____________________________
    # | past(0행)   |  문장  |  ...
    # | __________________________
    # | present(1행)|  문장  |  ...
    # | __________________________
    # | future(2행) |  문장  |  ...
    # | __________________________

    special_future = 0  # '것','이'를 처리하기 위한 변수
    is_present_flag = True # 현재시제 판단 위한 변수
    for i in range(len(sentence)):
        # 미래시제 1: '것''이'
        if sentence[i][1].find('NNB') != -1:
            special_future = special_future + 1  # NNB 는 '것'이므로 ++함
        if sentence[i][1].find('VCP') != -1:
            special_future = special_future + 1  # VCP 는 '이'이므로 ++함
        if special_future == 2:  # '것'과 '이'가 모두 존재하면 미래 시제로 판단
            tense_table[2].append(sentence)
            is_present_flag = False
            break
        # 높임 표현(시, 십, 세, 심, 실)의 경우 처리
        if sentence[i][1].find('EP') != -1 \
                and not sentence[i][0].find('시') != -1 \
                and not sentence[i][0].find('십') != -1 \
                and not sentence[i][0].find('세') != -1 \
                and not sentence[i][0].find('실') != -1 \
                and not sentence[i][0].find('심') != -1:
            # 미래시제 2: '겠'
            if sentence[i][0].find('겠') != -1:
                tense_table[2].append(sentence)
                is_present_flag = False
            # 과거시제
            else:
                tense_table[0].append(sentence)
                is_present_flag = False
            break
    # 현재시제
    if is_present_flag == True:
        tense_table[1].append(sentence)
    return tense_table
    # 추가 사항
    # '먹을 것이다'와 '먹는 것이다'를 구별할 수가 없음.
    # -> 파이썬 jamo 패키지 사용하면 초중종성 분리해서 'ㄹ' 찾아서 미래 처리 가능

# 시제를 플래그로 변환하는 함수
def tense_to_flag(sentence):
    # past    : 0
    # present : 1
    # future  : 2
    tense_table = find_tense(sentence)
    tense_flag = []
    for i in range(len(tense_table)):
        # 길이가 2 이상이어야 문장이 있는 것임
        if len(tense_table[i]) > 1:
            if tense_table[i][0] == 'past':
                tense_flag.append(0)
            elif tense_table[i][0] == 'future':
                tense_flag.append(2)
            else:
                tense_flag.append(1)
    return tense_flag

# 부정표현 flag
# 못, 안, 않, 말/마, 아니, 없 처리
# 부정표현 개수가 홀수이면 부정(1), 짝수이면 이중 부정이므로 긍정(0)
def find_neg(sentence):
    neg_flag = []  # 부정표현 flag를 저장할 배열(1:부정, 0:긍정)
    neg_cnt = 0  # 부정표현 개수를 세기 위한 변수
    for i in range(len(sentence)):
        if is_have_char('못', sentence[i]):
            neg_cnt = neg_cnt + 1
        if is_have_char('안', sentence[i]):
            neg_cnt = neg_cnt + 1
        if is_have_char('않', sentence[i]):
            neg_cnt = neg_cnt + 1
        if (is_have_char('말', sentence[i]) or is_have_char('마', sentence[i])) \
                and is_have_tag('VX', sentence[i]):
            neg_cnt = neg_cnt + 1
        if is_have_char('아니', sentence[i]):
            neg_cnt = neg_cnt + 1
        if is_have_char('없', sentence[i]):
            neg_cnt = neg_cnt + 1

    if neg_cnt % 2 == 1:  # 부정
        neg_flag.append(1)
    else:
        neg_flag.append(0)  # 긍정

    return neg_flag