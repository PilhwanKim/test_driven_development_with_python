from unittest import skip
from .base import FunctionalTest


class ItemValidationTest(FunctionalTest):
    @skip
    def test_cannot_add_empty_list_items(self):
        # 에디스는 메인 페이지에 접속해서 빈 아이템을 실수로 등록하려고 한다.
        # 입력 상자가 비어있는 상태에서 엔터키를 누른다.

        # 페이지가 새로 고침되고, 빈 아이템을 등록할 수 없다는 
        # 에러 메시지가 표시된다

        # 다른 아이템을 입력하고 이번에는 정상 처리된다

        # 그녀는 고의적으로 다시 빈 아이템을 등록한다.

        # 리스트 페이지에 다시 에러 메시지가 표시된다.

        # 아이템을 입력하면 정상 동작한다.
        self.fail('write me!')
