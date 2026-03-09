from django.shortcuts import render
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from vendor.models import Vendor


def get_or_set_current_location(request):
    if 'lat' in request.session:
        return request.session['lat'], request.session['lng']
    elif 'lat' in request.GET and 'lng' in request.GET:
        lat = request.GET['lat']
        lng = request.GET['lng']
        request.session['lat'] = lat
        request.session['lng'] = lng
        return lat, lng
    return None

def home(request):
    lat, lng = get_or_set_current_location(request)
    if lat and lng:
        point = GEOSGeometry('POINT(%s %s)' % (lng, lat))
        vendors = Vendor.objects.filter(user_profile__location__dwithin=(point, D(km=100))).annotate(distance=Distance('user_profile__location', point)).order_by('distance')

        for v in vendors:
            v.kms = round(v.distance.km, 1)
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    
    return render(request, 'home.html', {'vendors': vendors})