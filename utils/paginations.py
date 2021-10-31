from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FriendshipPagination(PageNumberPagination):

    # http://localhost/api/friendships/1/followers/page=2&size=10
    # APP和Web显示的信息数量不等。

    page_size = 20
    page_size_query_param = 'size'
    max_page_size = 20

    # 当我完成翻页的功能之后，对返回给前端的数据进行包装。
    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_next_page': self.page.has_next(),
            'results': data,
        })
