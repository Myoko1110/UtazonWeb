from django.shortcuts import redirect, render
from login.functions import check_session


def IndexView(request):

    if check_session(request):
        # 既ログイン処理
        return render(request, 'index.html')
    elif check_session(request) == "Expired session":
        # 期限切れ処理
        return render(request, 'index.html')
    else:
        # 未ログイン処理
        return redirect('/login')
