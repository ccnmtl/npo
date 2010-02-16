from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from npo_curve.curve import get_curve

def curve(request):
    x = [float(i) for i in request.GET.getlist('x')]
    y = [float(i) for i in request.GET.getlist('y')]
    xl = request.GET.get('xLabel', '')
    yl = request.GET.get('yLabel', '')
    dpi = int(request.GET.get('dpi', '500'))
    title = request.GET.get('title', '')
    data = get_curve(x, y, 1.5, dpi, xl, yl, title)
    return HttpResponse(data, content_type="image/jpeg")
