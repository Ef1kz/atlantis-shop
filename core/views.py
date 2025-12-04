from django.shortcuts import render

def home(request):
    categories = [
        {"name": "ВАННЫ", "slug": "vanny"},
        {"name": "РАКОВИНЫ", "slug": "rakoviny"},
        {"name": "УНИТАЗЫ И БИДЕ", "slug": "unitazy-i-bide"},
        {"name": "СМЕСИТЕЛИ", "slug": "smesiteli"}
    ]
    return render(request, 'home.html', {'categories': categories})