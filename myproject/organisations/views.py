from django.db.models import Q
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Organisation

ALLOWED_SORT_FIELDS = {'created_at', 'name'}


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['id', 'name', 'created_at']


class OrganisationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


class OrganisationListView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort = request.GET.get('sort', '-created_at').strip()
        law_firm_id = request.GET.get('law_firm_id', '').strip()

        sort_field = sort.lstrip('-')
        if sort_field not in ALLOWED_SORT_FIELDS:
            sort = '-created_at'

        qs = Organisation.objects.all()

        if law_firm_id:
            try:
                qs = qs.filter(law_firm_id=int(law_firm_id))
            except ValueError:
                pass

        if search:
            qs = qs.filter(Q(name__icontains=search))

        qs = qs.order_by(sort)

        paginator = OrganisationPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = OrganisationSerializer(page, many=True)

        return Response({
            'status': True,
            'message_code': 1000,
            'message': 'Operation completed successfully',
            'data': {
                'organisations': serializer.data,
                'pagination': {
                    'total': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
            },
            'errors': {},
        })
