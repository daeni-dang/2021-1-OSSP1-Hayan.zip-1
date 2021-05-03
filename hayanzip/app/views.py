from django.shortcuts import render

# Create your views here.

def main(request):
    if request.method == 'POST':
        text = request.POST['inputStr']
        print(text)
        return render(request, 'app/main.html', {'text': text})
    return render(request,'app/main.html')