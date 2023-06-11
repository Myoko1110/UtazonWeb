from django.shortcuts import redirect, render
from login.functions import session_is_valid


def IndexView(request):

    if session_is_valid(request)[0]:
        # 既ログイン処理
        return render(request, 'index.html', context={"session": False})
    elif session_is_valid(request)[1]:
        # 期限切れ処理
        return render(request, 'index.html', context={"session": False})
    else:
        # 未ログイン処理
        return redirect('/login')


def Item(request):
    return render(request, 'item.html')
