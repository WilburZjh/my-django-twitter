from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from dateutil import parser


class EndlessPagination(BasePagination):
    page_size = 20

    def __init__(self):
        super(EndlessPagination, self).__init__()
        self.has_next_page = False

    # 'to_html() must be implemented to display page controls.'
    def to_html(self):
        pass

    def paginate_ordered_list(self, reverse_ordered_list, request):
        if 'created_at__gt' in request.query_params:
            created_at__gt = parser.isoparse(request.query_params['created_at__gt'])
            objects = []
            for obj in reverse_ordered_list:
                if obj.created_at > created_at__gt:
                    objects.append(obj)
                else:
                    break
            self.has_next_page = False
            return objects

        index = 0
        if 'created_at__lt' in request.query_params:
            created_at__lt = parser.isoparse(request.query_params['created_at__lt'])
            for index, obj in enumerate(reverse_ordered_list):
                if obj.created_at < created_at__lt:
                    break
            else:
                # 如果上面的for 没有执行到break，则运行else
                # 没找到任何满足条件的 objects, 返回空数组
                # 注意这个 else 对应的是 for，参见 python 的 for else 语法
                reverse_ordered_list = []
        self.has_next_page = len(reverse_ordered_list) > index + self.page_size
        return reverse_ordered_list[index: index + self.page_size]

    # 'paginate_queryset() must be implemented.'
    def paginate_queryset(self, queryset, request, view=None):

        if type(queryset) == list:
            return self.paginate_ordered_list(queryset, request)

        if 'created_at__gt' in request.query_params:
            # created_at__gt 用于下拉刷新的时候加载最新的内容进来
            # 为了简便起见，下拉刷新不做翻页机制，直接加载所有更新的数据
            # 因为如果数据很久没有更新的话，不会采用下拉刷新的方式进行更新，而是重新加载最新的数据
            created_at__gt = request.query_params['created_at__gt']
            queryset = queryset.filter(created_at__gt=created_at__gt)
            self.has_next_page = False
            return queryset.order_by('-created_at')

        if 'created_at__lt' in request.query_params:
            # created_at__lt 用于向上滚屏（往下翻页）的时候加载下一页的数据
            # 寻找 created_at < created_at__lt 的 objects 里按照 created_at 倒序的前
            # page_size + 1 个 objects
            # 比如目前的 created_at 列表是 [10, 9, 8, 7 .. 1] 如果 created_at__lt=10
            # page_size = 2 则应该返回 [9, 8, 7]，多返回一个 object 的原因是为了判断是否
            # 还有下一页从而减少一次空加载。
            created_at__lt = request.query_params['created_at__lt']
            queryset = queryset.filter(created_at__lt=created_at__lt)

        queryset = queryset.order_by('-created_at')[:self.page_size + 1]
        self.has_next_page = len(queryset) > self.page_size
        return queryset[:self.page_size]

    # 'get_paginated_response() must be implemented.'
    def get_paginated_response(self, data):
        return Response({
            'has_next_page': self.has_next_page,
            'results': data,
        })
