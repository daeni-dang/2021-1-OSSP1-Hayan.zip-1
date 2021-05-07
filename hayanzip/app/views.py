from django.shortcuts import render
from eunjeon import Mecab


# Create your views here.

def main(request):
    if request.method == 'POST':
        str = request.POST.get('final_str', None)
        if str == None:  # 대본 입력됐을 경우
            text = request.POST['inputStr']
            script_table = sentence_division(text) #형태소 포함된 배열
            script_string_array = sentence_without_part(text, script_table) #형태소 없는 배열
            return render(request, 'app/main.html', {'text': text, 'script_string_array': script_string_array})
        else:
            sentence_division(str)  # 음성인식 됐을 경우
    return render(request, 'app/main.html')


def add_space_after_mot(input_string):  # '못' 뒤에 띄어쓰기 추가하는 함수 : '못'을 기준으로 split한 후, 각 요소 사이에 '못+공백'을 추가하여 합침.
    split_neg = input_string.split('못')
    for i in range(len(split_neg)):
        string = '못 '.join(split_neg)
    return string


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


def is_type_of_V(token):
    if token[1].find('V') != -1:
        return True
    else:
        return False


def is_NNG(token):
    if token[1].find('NNG') != -1:
        return True
    else:
        return False

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
    find_s(string_table)
    find_o(string_table)
    find_tense(string_table)

    # 문제! : 다은이 -> 다(MAG) + 은이(NNG) : MAG 삭제
    return string_table

def find_verb(string_table):
    for i in range(0, len(string_table)):
        start_flag = -1  # 서술어의 시작 플래그 초기화
        for j in range(0, len(string_table[i])):
            if start_flag == -1 and is_type_of_V(string_table[i][j]):  # 문장 요소에 V가 있다면
                start_flag = j  # 시작 플래그는 현재 토큰 index
            elif is_NNG(string_table[i][j]):  # 문장 요소에 N이 있다면
                start_flag = -1  # 서술어가 아니므로 start_flag = -1
        if start_flag != -1:  # start_flag가 -1이면 서술어가 없다는 것
            if start_flag > 0:  # start flag가 0이라면 앞에 것 볼 필요X
                if is_NNG(string_table[i][start_flag - 1]):  # start_flag 앞의 토큰이 명사라면
                    start_flag -= 1  # 시작 플래그를 하나 줄인다.
            print('V:', end=' ')
            for k in range(start_flag, len(string_table[i])):  # start_flag부터 끝까지 서술어
                print(string_table[i][k], end=' ')
            print()


# 보어를 찾는 함수 : 보격 조사를 찾고 보격 조사 앞에 있는 단어 + 보격 조사를 보어로 반환
def find_complement(input_string):  # ('되다'의 경우 현재 보격 조사 판별 X)
    mecab = Mecab()
    temp_string = mecab.pos(input_string)
    complementArr = []
    for i in range(len(temp_string)):
        if temp_string[i][1].find('JKC') != -1:  # 형태소 분석을 한 결과에서 보격 조사를 찾음
            complementArr.append(temp_string[i - 1])
            complementArr.append(temp_string[i])  # 보격 조사와 그 앞의 단어가 보어이므로 두 개 모두 list에 넣어줌
    return complementArr  # 한 문장 안에 보어가 여러 개가 될 수 있으므로 list의 형식으로 값을 반환


# 관형어를 찾는 함수 : 관형격 조사를 통해 관형어를 찾는 경우, 관형사를 관형어로 찾는 경우, 관형형 전성어미를 통해 관형어를 찾는 경우로 구성
def find_tubular(input_string):  # (체언 단독의 경우(ex.우연히 고향 친구를 만났다)와 체언의 자격을 가진 말 + 관형격 조사의 경우(ex.그는 웃기기의 천재다) 아직 처리 X)
    mecab = Mecab()
    temp_string = mecab.pos(input_string)
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

        # 체언의 자격을 가진 말 + 관형격 조사의 경우(ex.그는 웃기기의 천재다)에 대한 코드(아직 수정-ing)
        # if temp_string[i][1].find('JKG') != -1:
        #     jkgWord = temp_string[i][0]
        #     inputIndex = input_string.find(jkgWord)
        #     tubularTemp = ""
        #     for j in reversed(range(inputIndex)):
        #         if input_string[j] != ' ':
        #             tubularTemp = tubularTemp + input_string[j]
        #         elif input_string[j] == ' ':
        #             break
        #         elif j == 0:
        #             break
        #     tt = tubularTemp[::-1]
        #     print(tt)
        #     for k in range(len(temp_string)):
        #         if temp_string[k][0].find(tt[0]) != -1:
        #             while True:
        #                 print(temp_string[k])
        #                 if temp_string[k][1] == 'JKG':
        #                     break
        #                 k += 1

    return tubularArr  # 한 문장 안에 관형어는 여러 개가 될 수 있으므로 list의 형식으로 값을 반환

# 주어 찾는 함수
def find_s(string_table):
    s_table=[] #주어들만 저장할 테이블
    cnt=0
    jx_cnt=0
    for i in range(len(string_table)): #테이블 전체에서
        for k in range(len(string_table[i])):  #테이블에 저장된 한 문장 길이 동안
            if ((string_table[i][k][0] =='가'and string_table[i][k][1] =='JKS') or (string_table[i][k][0] =='이'and string_table[i][k][1] =='JKS')):
                #가,이 중 주격 조사인 것들에 한해
                for m in range(0, k-1): #주격 조사 앞에 있는 것들중
                    if (string_table[i][m][1]=='NNG' or string_table[i][m][1]=='NNP'or string_table[i][m][1]=='NNB' or string_table[i][m][1]=='NP'):
                        #명사에 해당 되는 것들 중에
                        cnt=m    # 가장 주격 조사에 가까운 것을
                s_table.append(string_table[i][cnt])  #주어라고 저장
               # s_table.append(string_table[i][k])   #주어 뒤에 조사(확인용)

            if ((string_table[i][k][0] =='은'and string_table[i][k][1] =='JX') or (string_table[i][k][0] =='는'and string_table[i][k][1] =='JX')):
                #은, 는 중 보조사 인것들에 한해
                jks_cnt = -1 # 주격조사count변수
                for x in range(len(string_table[i])):# 테이블의 i번째 문장 길이동안
                    if (string_table[i][x][1]=='JKS'): # jsk(주격 조사가 있으면)
                        jks_cnt +=1  #count변수++
                if (jks_cnt<0): #만약 주격 조사가 없으면
                    for z in range(0, k - 1):  # 은, 는 앞에 있는 것들중
                        if (string_table[i][z][1] == 'NNG' or string_table[i][z][1] == 'NNP' or string_table[i][z][1] == 'NNB' or string_table[i][z][1] == 'NP'):
                                # 명사에 해당 되는 것들 중에
                            jx_cnt = z  # 가장 주격 조사에 가까운 것을
                    s_table.append(string_table[i][jx_cnt])# 주어라고 저장
                   # s_table.append(string_table[i][k])   #주어 뒤에 조사(확인용)
    print("주어:")
    for j in range(len(s_table)):
        print(s_table[j])

    return s_table

#목적어 찾는 함수
def find_o(string_table):
    cnt=0
    o_table=[] #목적어들만 저장할 테이블
    for i in range(len(string_table)):#문장 테이블 전체에서
        for k in range(len(string_table[i])):# 문장 한문장 안에
            if ((string_table[i][k][0] =='을' and string_table[i][k][1] =='JKO') or (string_table[i][k][0] =='를'and string_table[i][k][1] =='JKO')):
                #을를 인데 목적격 조사인 것이 나오면
                o_table.append(string_table[i][k-1])# 목적어 라고 저장
                #o_table.append(string_table[i][k])# 목적어 뒤에 조사(확인용)

            if ((string_table[i][k][0] =='은'and string_table[i][k][1] =='JX') or (string_table[i][k][0] =='는'and string_table[i][k][1] =='JX')):
                #은 는 인데 보조사 인 경우
                jks_cnt = -1 # 주격조사를 count
                for x in range(len(string_table[i])):  # 테이블의 i번째 문장 길이동안
                    if (string_table[i][x][1] == 'JKS'):  # jsk(주격 조사가 있으면)
                        jks_cnt += 1  # count변수++
                if (jks_cnt>=0): #주격 조사가 있으면
                    o_table.append(string_table[i][k - 1]) #조사 앞을 목적어라고 저장
                    #o_table.append(string_table[i][k]) #목적어 뒤에 조사(확인용)

    print("목적어:")
    for j in range(len(o_table)):
        print(o_table[j])

    return o_table

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

# 시제 찾는 함수
def find_tense(string_table):
    tense_table = [] # 문자열과 시제를 함께 저장할 테이블
    for i in range(len(string_table)):
        special_future = 0 # '것','이'를 처리하기 위한 변수
        for j in range(len(string_table[i])):
            # 미래시제 1: '것''이'
            if is_have_tag('NNB', string_table[i][j]):
                special_future = special_future + 1 # NNB 는 '것'이므로 ++함
            if is_have_tag('VCP', string_table[i][j]):
                special_future = special_future + 1 # VCP 는 '이'이므로 ++함
            if special_future == 2: # '것'과 '이'가 모두 존재하면 미래 시제로 판단
                tense_table.append(string_table[i])
                tense_table.append('future')
                break
            if is_have_tag('EP', string_table[i][j]):
                # 미래시제 2: '겠'
                if is_have_char('겠', string_table[i][j]):
                    tense_table.append(string_table[i])
                    tense_table.append('future')
                # 과거시제
                else:
                    tense_table.append(string_table[i])
                    tense_table.append('past')
                # print(string_table[i][j])
                break

    return tense_table
    # 추가 사항
    # '먹을 것이다'와 '먹는 것이다'를 구별할 수가 없음.
    # -> 파이썬 jamo 패키지 사용하면 초중종성 분리해서 'ㄹ' 찾아서 미래 처리 가능