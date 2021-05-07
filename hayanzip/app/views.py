from django.shortcuts import render
from eunjeon import Mecab

# Create your views here.

def main(request):
    if request.method == 'POST':
        str = request.POST.get('final_str', None)
        if str == None :    #대본 입력됐을 경우
            text = request.POST['inputStr']
            sentence_division(text)
            return render(request, 'app/main.html', {'text': text})
        else:
            sentence_division(str) #음성인식 됐을 경우
    return render(request,'app/main.html')

def add_space_after_mot(input_string):      # '못' 뒤에 띄어쓰기 추가하는 함수 : '못'을 기준으로 split한 후, 각 요소 사이에 '못+공백'을 추가하여 합침.
    split_neg = input_string.split('못')
    for i in range(len(split_neg)):
        string = '못 '.join(split_neg)
    return string

def is_sentence_End(last_token):        # 문장의 마지막인지 판단 : EF[종결어미] 이거나 EC(연결어미)로 분석된 마지막 요소
    # find('str')는 str의 위치를 반환하는 함수. 없을 때는 -1 반환
    # 문장의 마지막 형태소일 때(즉, EF[종결어미]를 만났을 때)
    # 혹은 EC일 경우, '다','요','까'의 경우 종결어미로 인식
    if last_token[1].find('EF') != -1 \
            or last_token[1].find('EC') != -1:
        return True
    else:
        return False

def is_MAG_except_neg(token):       # '못', '안'을 제외한 MAG[일반 부사]인가 판단
    if token[1] == 'MAG':
        if token[0] != '못' and token[0] != '안':
            return True
    return False

def is_mark(token):          # 문장부호(. ? ! , · / : )인지 판단
    if token[1] == 'SF' or token[1] == 'SC':
        return True
    return False

def is_type_of_V(token):
    if token[1].find('V') != -1 :
        return True
    else:
        return False

def is_NNG(token):
    if token[1].find('NNG') != -1 :
        return True
    else:
        return False

def sentence_division(input_string):
    mecab = Mecab()

    input_string = add_space_after_mot(input_string)  # '못' 뒤에 띄어쓰기 추가

    string_table = []  # 한 문장씩 저장할 테이블
    mecab_result = mecab.pos(input_string)  # ex) [('안녕', 'NNG'), ('하', 'XSV'), ('세요', 'EP+EF')]

    string_start = 0  # 각 문장의 첫번째 요소 가르키는 변수
    for i in range(len(mecab_result)):
        if is_sentence_End(mecab_result[i]):  # 문장의 마지막인지 판단
            sentence = []
            for j in range(string_start, i + 1):  # 한 문장 내의 첫번째 요소부터 마지막 요소까지 저장.
                if is_MAG_except_neg(mecab_result[j]):  # '못', '안'을 제외한 MAG[일반 부사]는 저장 X
                    continue
                if is_mark(mecab_result[j]):  # 문장부호는 저장 X
                    continue
                sentence.append(mecab_result[j])  # 각 요소를 현재 문장에 추가
            string_table.append(sentence)  # 완성된 한 문장을 테이블에 추가
            string_start = i + 1  # 다음 문장의 첫 번째 요소를 가리킴.

    for i in range(len(string_table)):  # 테이블 출력
        print(string_table[i])
    find_verb(string_table)

    # 문제! : 다은이 -> 다(MAG) + 은이(NNG) : MAG 삭제


def find_verb(string_table):
    for i in range(0,len(string_table)):
        start_flag = -1  # 서술어의 시작 플래그 초기화
        for j in range(0,len(string_table[i])):
            if start_flag== -1 and is_type_of_V(string_table[i][j]): #문장 요소에 V가 있다면
                start_flag= j # 시작 플래그는 현재 토큰 index
            elif is_NNG(string_table[i][j]): #문장 요소에 N이 있다면
                start_flag= -1  #서술어가 아니므로 start_flag = -1
        if start_flag!=-1:  #start_flag가 -1이면 서술어가 없다는 것
            if start_flag>0: #start flag가 0이라면 앞에 것 볼 필요X
                if is_NNG(string_table[i][start_flag-1]): #start_flag 앞의 토큰이 명사라면
                    start_flag-=1 #시작 플래그를 하나 줄인다.
            print('V:', end=' ')
            for k in range(start_flag, len(string_table[i])): #start_flag부터 끝까지 서술어
                print(string_table[i][k], end=' ')
            print()