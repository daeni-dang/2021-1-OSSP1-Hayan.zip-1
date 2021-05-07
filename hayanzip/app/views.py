from django.shortcuts import render
from eunjeon import Mecab

# Create your views here.

def main(request):
    if request.method == 'POST':
        #text = request.POST['inputStr']
        #sentence_division(text)
        #return render(request, 'app/main.html', {'text': text})
        str = request.POST.get('final_str', None)
        if str == None :
            print("No str")
        else:
            sentence_division(str)
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
            or (last_token[1].find('EC') != -1
                and (last_token[0].find('다') != -1 or last_token[0].find('요') != -1 or last_token[0].find('까') != -1) ):
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

    # 문제! : 다은이 -> 다(MAG) + 은이(NNG) : MAG 삭제