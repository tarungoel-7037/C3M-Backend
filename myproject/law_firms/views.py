from django.db.models import Q
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import LawFirm

ALLOWED_SORT_FIELDS = {'created_at', 'name'}


class LawFirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawFirm
        fields = ['id', 'name', 'created_at']


class LawFirmPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


class LawFirmListView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort = request.GET.get('sort', '-created_at').strip()

        sort_field = sort.lstrip('-')
        if sort_field not in ALLOWED_SORT_FIELDS:
            sort = '-created_at'

        qs = LawFirm.objects.all()

        if search:
            qs = qs.filter(Q(name__icontains=search))

        qs = qs.order_by(sort)

        paginator = LawFirmPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = LawFirmSerializer(page, many=True)

        return Response({
            'status': True,
            'message_code': 1000,
            'message': 'Operation completed successfully',
            'data': {
                'law_firms': serializer.data,
                'pagination': {
                    'total': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
            },
            'errors': {},
        })
